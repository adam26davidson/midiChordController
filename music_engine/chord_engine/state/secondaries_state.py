from enum import Enum


class SecondarySide(Enum):

    LEFT = 1
    NONE = 2
    RIGHT = 3

class SecondariesState:

    side: SecondarySide

    def __init__(self) -> None:
        self.side = SecondarySide.NONE
