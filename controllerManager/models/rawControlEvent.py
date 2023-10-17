from enum import Enum

from controllerManager.models.mappableControlEvent import MappableControlEvent

class RawControlEvent(Enum):
    ON = 1
    OFF = 2
    RIGHT = 3
    LEFT = 4
    UP = 5
    DOWN = 6
    UPDATE = 7