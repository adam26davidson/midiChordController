from enum import Enum


class ChordButton(Enum):
    SOUTH = "south"
    WEST = "west"
    NORTH = "north"
    EAST = "east"

class ChordsState:

    root_class: int = 0
    note_classes: list[int] = []
    playing_notes: list[int] = []
    is_playing: bool = False
    active_button: ChordButton = ChordButton.SOUTH
    button_queue: list[int] = []
