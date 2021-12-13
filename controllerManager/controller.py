from abc import ABC, abstractmethod, abstractproperty
import evdev

class Controller(ABC):

  def __init__(self, sendEvent, info, state):
    self.sendEvent = sendEvent
    self.info = info
    self.state = state

  
  @abstractmethod
  def start(self):
    pass

  def checkIfConnected(self):
    pass

  @abstractmethod
  def getUIMap(self):
    pass

  @abstractmethod
  def getMusicEngineMap(self):
    pass

  @staticmethod
  def checkIfConnected(info):
    found = False
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
      vendorMatch = device.info.vendor == info['vendor']
      productMatch = device.info.product == info['product']
      if (vendorMatch and productMatch):
        found = True
    return found

  def createState(self, controls):
    state = {}
    for control in controls:
      if control['type'] in ['BUTTON', "PAD"]:
        state[control['name']] = 0
      elif control['type'] == 'ANALOG':
        state[control['name']] = {"valueHistory": [], "thresholdValue": 0}
    return state

  def processEvent(self, event, device):
    if event.code in self.info['controls'][device].keys():

      control = self.info['controls'][device][event.code]
      controlState = self.state[control['name']]

      if control['type'] in ['BUTTON', 'PAD']:
        self.processButtonEvent(event, control, controlState)
      elif control['type'] == 'ANALOG':
        self.processAnalogEvent(event, control, controlState)

  def processButtonEvent(self, event, control, controlState):
    controlState[control['name']] = event.value
    eventName = control['events'][event.value]
    self.sendEvent({'name': eventName})

  def processAnalogEvent(self, event, control, controlState):
    range = control['range']
    config = control['config']

    # update value history
    valueHistory = controlState["valueHistory"]
    valueHistory.append(event.value)
    if (len(valueHistory) > config["averageCount"]):
      valueHistory.pop(0)

    # get the average of the past raw values (prevents fluttering)
    sum = 0
    for val in valueHistory:
      sum += val
    averageValue = sum / len(valueHistory)

    #normalize value to between -0.999 and 0.999
    slope = 2.0 / (range["top"]- range["bottom"])
    intercept = 1 - (slope * range["top"])
    normalizedValue =  (slope * averageValue) + intercept
    normalizedValue = max(min(normalizedValue, 0.999), -0.999)
      
    self.sendEvent({
      'name': control['events']['value'],
      'value': normalizedValue
    })

    self.processThreshold(normalizedValue, control, controlState)

  def processThreshold(self, normalizedValue, control, controlState):
    if 'threshold' in control['events'].keys():
      thresholdValue = 0
      if "centeredThreshold" in control['config'].keys():
        if normalizedValue > control['config']["centeredThreshold"]:
          thresholdValue = 1
        elif normalizedValue < -1*control['config']["centeredThreshold"]:
          thresholdValue = -1
      elif "centeredThreshold" in control['config'].keys():
        threshold = -1 + (control['config']["centeredThreshold"] * 2)
        if normalizedValue > threshold:
          thresholdValue = 1
        else:
          thresholdValue = 0

      thresholdValueChanged = thresholdValue != controlState["thresholdValue"]

      # update threshold state
      controlState["thresholdValue"] = thresholdValue

      if thresholdValueChanged:
        eventName = control['events']['threshold'][thresholdValue]
        self.sendEvent({'name': eventName})