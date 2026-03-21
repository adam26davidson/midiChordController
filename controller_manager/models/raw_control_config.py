from __future__ import annotations

from controller_manager.models.polar_orientation import PolarOrientation

from .raw_control_event import RawControlEvent


class RawControlConfig:
    top_value: int
    bottom_value: int

    expose_on_off_events: bool
    expose_polar_events: bool

    average_count: int
    ignore_values: list[int]

    centered_threshold: float
    threshold: float

    polar_event_map: dict[int, RawControlEvent]
    polar_orientation: PolarOrientation

    def __init__(self,
                 top_value: int | None = None,
                 bottom_value: int | None = None,
                 expose_on_off_events: bool | None = None,
                 expose_polar_events: bool | None = None,
                 average_count: int | None = None,
                 centered_threshold: float | None = None,
                 threshold: float | None = None,
                 ignore_values: list[int] | None = None,
                 polar_event_map: dict[int, RawControlEvent] | None = None,
                 polar_orientation: PolarOrientation | None = None):
        self.top_value = top_value
        self.bottom_value = bottom_value
        self.expose_on_off_events = expose_on_off_events
        self.expose_polar_events = expose_polar_events
        self.average_count = average_count
        self.centered_threshold = centered_threshold
        self.threshold = threshold
        self.ignore_values = ignore_values
        self.polar_event_map = polar_event_map
        self.polar_orientation = polar_orientation
