from __future__ import annotations

from controllerManager.models.polarOrientation import PolarOrientation

from .rawControlEvent import RawControlEvent


class RawControlConfig:
    topValue: int
    bottomValue: int

    exposeOnOffEvents: bool
    exposePolarEvents: bool

    averageCount: int
    ignoreValues: list[int]

    centeredThreshold: float
    threshold: float

    polarEventMap: dict[int, RawControlEvent]
    polerOrientation: PolarOrientation

    def __init__(self,
                 topValue: int | None = None,
                 bottomValue: int | None = None,
                 exposeOnOffEvents: bool | None = None,
                 exposePolarEvents: bool | None = None,
                 averageCount: int | None = None,
                 centeredThreshold: float | None = None,
                 threshold: float | None = None,
                 ignoreValues: list[int] | None = None,
                 polarEventMap: dict[int, RawControlEvent] | None = None,
                 polarOrientation: PolarOrientation | None = None):
        self.topValue = topValue
        self.bottomValue = bottomValue
        self.exposeOnOffEvents = exposeOnOffEvents
        self.exposePolarEvents = exposePolarEvents
        self.averageCount = averageCount
        self.centeredThreshold = centeredThreshold
        self.threshold = threshold
        self.ignoreValues = ignoreValues
        self.polarEventMap = polarEventMap
        self.polarOrientation = polarOrientation
