from controllerManager.models.mappableControl import MappableControl
from controllerManager.models.mappableControlEvent import MappableControlEvent


class ControlEvent():
    controlKey: str
    event: MappableControlEvent
    value: float
    controllerId: str

    def __init__(
            self, 
            controlKey: str, 
            event: MappableControlEvent, 
            controllerId: str,
            value: float = None):
        
        self.controlKey = controlKey
        self.event = event
        self.controllerId = controllerId
        self.value = value