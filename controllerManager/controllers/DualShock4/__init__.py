import evdev
import asyncio
from .controls import controls
from ...controller import Controller

class DualShock4(Controller):

  def __init__(self, sendEvent):

    mainState = self.createState(self.controls['main'])
    motionState = self.createState(self.controls['motion'])
    touchState = self.createState(self.controls['touch'])
    state = mainState | motionState | touchState

    super.__init__(sendEvent, controls, state)

  def start(self):
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
      vendorMatch = device.info.vendor == controls['vendor']
      productMatch = device.info.product == controls['product']
      if (vendorMatch and productMatch):
        if (device.name.lower().find('motion') != -1):
          self.motion = evdev.InputDevice(device.path)
          asyncio.ensure_future(self.motionLoop())
        elif (device.name.lower().find('touchpad') != -1):
          self.touch = evdev.InputDevice(device.path)
          asyncio.ensure_future(self.touchLoop())
        else:
          self.mainControls = evdev.InputDevice(device.path)
          asyncio.ensure_future(self.mainControlsLoop())

  def checkIfConnected():
      found = False
      devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
      for device in devices:
        vendorMatch = device.info.vendor == controls['vendor']
        productMatch = device.info.product == controls['product']
        if (vendorMatch and productMatch):
          found = True
      return found
  
  async def mainControlsLoop(self):
    async for event in self.mainControls.async_read_loop():
      self.processEvent(event, 'main')

  async def motionLoop(self):
    async for event in self.motion.async_read_loop():
      self.processEvent(event, 'motion')

  async def touchLoop(self):
    async for event in self.touch.async_read_loop():
      self.processEvent(event, 'touch')
