import evdev
import asyncio
from .config import config
from ...controller import Controller

class DualShock4(Controller):

  config = config

  def __init__(self, sendEvent):
    self.sendEvent = sendEvent

    mainState = self.createState(self.config['main'])
    motionState = self.createState(self.config['motion'])
    touchState = self.createState(self.config['touch'])
    self.state = mainState | motionState | touchState
  
  def createState(self, controls):
    state = {}
    for control in controls:
      if control['type'] in ['BUTTON', "PAD"]:
        state[control['name']] = 0
      elif control['type'] == 'ANALOG':
        state[control['name']] = {"valueHistory": [], "thresholdValue": 0}

  def start(self):
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
      if (device.name == "Wireless Controller"):
        self.mainControls = evdev.InputDevice(device.path)
        asyncio.ensure_future(self.mainControlsLoop())
      elif (device.name == "Wireless Controller Motion Sensors"):
        self.motion = evdev.InputDevice(device.path)
        asyncio.ensure_future(self.motionLoop())
      elif (device.name == "Wireless Controller Touchpad"):
        self.touch = evdev.InputDevice(device.path)
        asyncio.ensure_future(self.touchLoop())

      self.display.setController(self.config["name"])
    super().start()

  def checkIfConnected():
      found = False
      devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
      for device in devices:
        if (device.name == "Wireless Controller"):
          found = True
        elif (device.name == "Wireless Controller Motion Sensors"):
          found = True
        elif (device.name == "Wireless Controller Touchpad"):
          found = True
      return found

  def processEvent(self, event, device):
    if event.code in self.config[device].keys():
      control = self.config['main'][event.code]
      if control['type'] in ['BUTTON', 'PAD']:
        self.processButtonEvent(event, device)
      elif control['type'] == 'ANALOG':
        self.processAnalogEvent(event, device)

  def processButtonEvent(self, event, device):
    control = self.config[device][event.code]

    self.state[control['name']] = event.value
    eventName = control['events'][event.value]
    self.sendEvent({'name': eventName})

  def processAnalogEvent(self, event, device):
    control = self.config[device][event.code]
    state = self.state[control['name']]

    result = self.processAnalogValue(event.value, control, state)
    state = result['state']

    self.sendEvent({
      'name': control['events']['value'],
      'value': result['value']
    })

    if result['thresholdValueChanged']:
      eventName = control['events']['threshold'][result['thresholdValue']]
      self.sendEvent({'name': eventName})
  
  async def mainControlsLoop(self):
    async for event in self.mainControls.async_read_loop():
      self.processEvent(event, 'main')

  async def motionLoop(self):
    async for event in self.motion.async_read_loop():
      self.processEvent(event, 'motion')

  async def touchLoop(self):
    async for event in self.touch.async_read_loop():
      self.processEvent(event, 'touch')
