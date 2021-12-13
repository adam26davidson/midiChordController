import evdev
import asyncio
from .info import info
from ...controller import Controller

class DualShock4(Controller):

  def __init__(self, sendEvent):

    state = {} 
    for device in info['controls'].keys():
      state = state | self.createState(self.info['controls'][device])

    super.__init__(sendEvent, info, state)

  def start(self):
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    foundDevice = False
    for device in devices:
      vendorMatch = device.info.vendor == info['vendor']
      productMatch = device.info.product == info['product']
      
      if (vendorMatch and productMatch):
        if not foundDevice:
          self.id = device.uniq
          foundDevice = True
        isCorrectId = device.uniq == self.id
        if (device.name.lower().find('motion') != -1 and isCorrectId):
          self.motionDevice = evdev.InputDevice(device.path)
          asyncio.ensure_future(self.createReadLoop('motion'))
        elif (device.name.lower().find('touchpad') != -1 and isCorrectId):
          self.touchDevice = evdev.InputDevice(device.path)
          asyncio.ensure_future(self.createReadLoop('touch'))
        elif isCorrectId:
          self.mainDevice = evdev.InputDevice(device.path)
          asyncio.ensure_future(self.createReadLoop('main'))
          
  @staticmethod
  def checkIfConnected():
    return Controller.checkIfConnected(info)

  def createReadLoop(self, device):
    return lambda device : self.deviceLoop(device)

  async def deviceLoop(self, device):
    async for event in self.mainDevice.async_read_loop():
      self.processEvent(event, device)
