import evdev
from .info import info
from redux import store
from ...controller import Controller

class DualShock4(Controller):

  def __init__(self, sendEvent):
    super().__init__(sendEvent, info)

  def start(self):
    availableDevices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    foundDevice = False
    connectedControllers = store.get_state()['controllerManager']['controllers']
    connectedIds = [c['id'] for c in connectedControllers]
    devices = {}
    id = None
    for device in availableDevices:
      vendorMatch = device.info.vendor == info['vendor']
      productMatch = device.info.product == info['product']
      newId = device.uniq not in connectedIds
      if (vendorMatch and productMatch and newId):
        if not foundDevice:
          id = device.uniq
          foundDevice = True
        isCorrectId = device.uniq == id
        if (device.name.lower().find('motion') != -1 and isCorrectId):
          devices['motion'] = device
        elif (device.name.lower().find('touchpad') != -1 and isCorrectId):
          devices['touch'] = device
          print('touchpad connected')
        elif isCorrectId:
          devices['main'] = device
    super().start(id, devices)

  @staticmethod
  def checkIfConnected():
    return Controller.checkIfConnected(info)

