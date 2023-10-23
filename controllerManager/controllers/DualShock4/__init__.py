import evdev
from .info import info, controllerConfig as config
from redux import store
from ...controller import Controller

class DualShock4(Controller):

    def __init__(self, sendEvent):
        super().__init__(sendEvent, info, config)
        self.id = None

    def open(self):
        availableDevices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        print(availableDevices)
        foundDevice = False
        connectedControllers = store.get_state()['controllerManager']['controllers']
        connectedIds = [c['id'] for c in connectedControllers]
        devices = {}
        id = None
        for device in availableDevices:
            vendorMatch = device.info.vendor == config.vendor
            productMatch = device.info.product == config.product
            newId = device.uniq not in connectedIds
            if (vendorMatch and productMatch and newId):
                if not foundDevice:
                    id = device.uniq
                    foundDevice = True
                isCorrectId = device.uniq == id
                if (device.name.lower().find('motion') != -1 and isCorrectId):
                    devices['motion'] = device
                    print(f"found motion device: {device.name}")
                elif (device.name.lower().find('touchpad') != -1 and isCorrectId):
                    devices['touch'] = device
                    print(f"found touch device: {device.name}")
                elif isCorrectId:
                    devices['main'] = device
                    print(f"found main device: {device.name}")
        super().open(id, devices)

    @staticmethod
    def checkForNewConnections():
        return Controller.checkForNewConnections(config)

