from enum import Enum


class ModulationSide(Enum):
    LEFT = 1
    NONE = 2
    RIGHT = 3

class ModulationsState:
    side: ModulationSide = ModulationSide.NONE
    buttonQueue: list[ModulationSide] = []
