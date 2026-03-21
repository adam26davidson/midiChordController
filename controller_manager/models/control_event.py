from __future__ import annotations

from controller_manager.models.mappable_control_event import MappableControlEvent


class ControlEvent:
    control_key: str
    event: MappableControlEvent
    value: float | None
    controller_id: str | None

    def __init__(
            self,
            control_key: str,
            event: MappableControlEvent,
            controller_id: str | None,
            value: float | None = None):

        self.control_key = control_key
        self.event = event
        self.controller_id = controller_id
        self.value = value
