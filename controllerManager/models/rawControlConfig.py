from typing import List, Dict
from controllerManager.models.mappableControlType import MappableControlType
from controllerManager.models.polarOrientation import PolarOrientation
from .rawControlEvent import RawControlEvent


class RawControlConfig():
    topValue: int
    bottomValue: int

    exposeOnOffEvents: bool
    exposePolarEvents: bool

    averageCount: int
    ignoreValues: List[int]

    centeredThreshold: float
    threshold: float

    polarEventMap: Dict[int, RawControlEvent]
    polerOrientation: PolarOrientation

    def __init__(self, 
                 topValue: int = None, 
                 bottomValue: int = None, 
                 exposeOnOffEvents: bool = None,
                 exposePolarEvents: bool = None,
                 averageCount: int = None, 
                 centeredThreshold: float = None, 
                 threshold: float = None,
                 ignoreValues: List[int] = None, 
                 polarEventMap: Dict[int, RawControlEvent] = None,
                 polarOrientation: PolarOrientation = None):
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