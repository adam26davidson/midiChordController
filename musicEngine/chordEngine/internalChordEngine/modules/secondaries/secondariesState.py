from enum import Enum
from typing import List


class SecondarySide(Enum):
    
    LEFT = 1
    NONE = 2
    RIGHT = 3

class SecondariesState():

    side: SecondarySide = SecondarySide.NONE
    buttonQueue: List[SecondarySide] = []