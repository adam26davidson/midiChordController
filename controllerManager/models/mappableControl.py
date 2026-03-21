from .mappableControlType import MappableControlType


class MappableControl:
    label: str
    key: str
    raw_control_key: str
    controller_id: str
    type: MappableControlType

    def __init__(self, label: str, key: str, raw_control_key: str, controller_id: str, type: MappableControlType):
        self.label = label
        self.key = key
        self.raw_control_key = raw_control_key
        self.controller_id = controller_id
        self.type = type
