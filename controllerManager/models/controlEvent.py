from __future__ import annotations

from controllerManager.models.mappableControlEvent import MappableControlEvent


class ControlEvent:
    controlKey: str
    event: MappableControlEvent
    value: float
    controllerId: str

    def __init__(
            self,
            controlKey: str,
            event: MappableControlEvent,
            controllerId: str,
            value: float | None = None):

        self.controlKey = controlKey
        self.event = event
        self.controllerId = controllerId
        self.value = value
