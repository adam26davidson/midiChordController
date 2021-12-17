from abc import ABC, abstractmethod, abstractproperty
import asyncio
from .maps import meMaps, uiMaps
from redux import store
from redux.actions import controllerManager as actions
import evdev

class Controller(ABC):

  def __init__(self, sendEvent, info):
    self.sendEvent = sendEvent
    self.info = info
    self.meMap = meMaps[self.info['meMap']]
    self.uiMap = uiMaps[self.info['uiMap']]

    state = {} 
    for device in info['controls'].keys():
      state = {**state, **self.createState(self.info['controls'][device])}
    
    self.state = state

  @staticmethod
  def checkIfConnected(info):
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    connectedControllers = store.get_state()['controllerManager']['controllers']
    connectedIds = [c['id'] for c in connectedControllers]
    for device in devices:
      vendorMatch = device.info.vendor == info['vendor']
      productMatch = device.info.product == info['product']
      newId = device.uniq not in connectedIds
      if (vendorMatch and productMatch and newId):
        return True
    return False

  def start(self, id, devices):
    self.id = id
    self.devices = devices
    connectedControllers = store.get_state()['controllerManager']['controllers']
    roles = [c['role'] for c in connectedControllers]
    role = 'primary'
    if 'primary' in roles: role = 'secondary'
    for key in devices.keys():
      asyncio.ensure_future(self.deviceReadLoop(key))
    data = {
      'id': id, 
      'name': self.info['name'],
      'role': role,
      'meMap': self.meMap,
      'uiMap': self.uiMap,
      'compatibleMeMaps': self.info['compatibleMeMaps']
    }
    store.dispatch(actions.add(data))

  async def deviceReadLoop(self, device):
    async for event in self.devices[device].async_read_loop():
      self.processEvent(event, device)

  def createState(self, controls):
    state = {}
    for control in controls.values():
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
        self.processButtonEvent(event, control)
      elif control['type'] == 'ANALOG':
        self.processAnalogEvent(event, control, controlState)

  def processButtonEvent(self, event, control):
    eventName = control['events'][event.value]
    self.sendEvent({'name': eventName, 'id': self.id})
    self.state[control['name']] = event.value

  def processAnalogEvent(self, event, control, controlState):
    range = control['range']
    config = control['config']

    ignoreValue = False
    if 'ignoreValues' in config.keys():
      if event.value in config['ignoreValues']:
        ignoreValue = True

    if not ignoreValue:

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
        'id': self.id,
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
        self.sendEvent({'name': eventName, 'id': self.id})