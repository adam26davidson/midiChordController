import evdev
from .info import info
from redux import store
from ...controller import Controller

class Wired360Controller(Controller):
    def __init__(self, sendEvent):
        super().__init__(sendEvent, info)

    def start(self):
        availableDevices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        connectedControllers = store.get_state()['controllerManager']['controllers']
        connectedIds = [c['id'] for c in connectedControllers]
        devices = {}
        id = None
        for device in availableDevices:
            vendorMatch = device.info.vendor == info['vendor']
            productMatch = device.info.product == info['product']
            newId = device.uniq not in connectedIds
            if (vendorMatch and productMatch and newId):
                devices['main'] = device
                id = device.uniq
        super().start(id, devices)

    @staticmethod
    def checkIfConnected():
        return Controller.checkIfConnected(info)

    