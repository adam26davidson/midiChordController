import evdev

from redux import store

from ...controller import Controller
from .info import info


class Wired360Controller(Controller):
    def __init__(self, send_event):
        super().__init__(send_event, info)

    def open(self):
        available_devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        connected_controllers = store.get_state()['controllerManager']['controllers']
        connected_ids = [c['id'] for c in connected_controllers]
        devices = {}
        id = None
        for device in available_devices:
            vendor_match = device.info.vendor == info['vendor']
            product_match = device.info.product == info['product']
            new_id = device.uniq not in connected_ids
            if (vendor_match and product_match and new_id):
                devices['main'] = device
                id = device.uniq
        super().open(id, devices)

    @staticmethod
    def check_for_new_connections():
        return Controller.check_for_new_connections(info)

