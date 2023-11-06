from enum import Enum


class InversionMode(Enum):
    INCREMENTAL = 1
    CONTINUOUS = 2

class InversionState():
    value: int = 0
    range: int = 4
    mode: InversionMode = InversionMode.INCREMENTAL
    locked: bool = False