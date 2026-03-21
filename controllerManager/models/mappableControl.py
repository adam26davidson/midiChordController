from .mappableControlType import MappableControlType


class MappableControl:
    label: str
    key: str
    rawControlKey: str
    controllerId: str
    type: MappableControlType

    def __init__(self, label: str, key: str, rawControlKey: str, controllerId: str, type: MappableControlType):
        self.label = label
        self.key = key
        self.rawControlKey = rawControlKey
        self.controllerId = controllerId
        self.type = type
