from enum import Enum


class SecondarySide(Enum):

    LEFT = 1
    NONE = 2
    RIGHT = 3

class SecondariesState:

    side: SecondarySide = SecondarySide.NONE
    button_queue: list[SecondarySide] = []
