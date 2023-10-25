from enum import Enum


class MappableControlEvent(Enum):
    ON = 1
    OFF = 2
    POSITIVE = 3
    NEGATIVE = 4
    UPDATE = 5