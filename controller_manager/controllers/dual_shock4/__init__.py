import evdev

from redux import get_controller_manager_state

from ...controller import Controller
from .info import controller_config as config
from .info import info


class DualShock4(Controller):

    def __init__(self, send_event):
        super().__init__(send_event, info, config)
        self.id = None

    def open(self):  # type: ignore[override]
        available_devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        print(available_devices)
        found_device = False
        connected_controllers = get_controller_manager_state()['controllers']
        connected_ids = [c['id'] for c in connected_controllers]
        devices = {}
        id = None
        for device in available_devices:
            vendor_match = device.info.vendor == config.vendor
            product_match = device.info.product == config.product
            new_id = device.uniq not in connected_ids
            if (vendor_match and product_match and new_id):
                if not found_device:
                    id = device.uniq
                    found_device = True
                is_correct_id = device.uniq == id
                if (device.name.lower().find('motion') != -1 and is_correct_id):
                    devices['motion'] = device
                    print(f"found motion device: {device.name}")
                elif (device.name.lower().find('touchpad') != -1 and is_correct_id):
                    devices['touch'] = device
                    print(f"found touch device: {device.name}")
                elif is_correct_id:
                    devices['main'] = device
                    print(f"found main device: {device.name}")
        if id is not None:
            super().open(id, devices, recording=False)

    @staticmethod
    def check_for_new_connections():  # type: ignore[override]
        return Controller.check_for_new_connections(config)
