from __future__ import annotations

from controllerManager.models.mappableControlEvent import MappableControlEvent


class ControlEvent:
    control_key: str
    event: MappableControlEvent
    value: float
    controller_id: str

    def __init__(
            self,
            control_key: str,
            event: MappableControlEvent,
            controller_id: str,
            value: float | None = None):

        self.control_key = control_key
        self.event = event
        self.controller_id = controller_id
        self.value = value
