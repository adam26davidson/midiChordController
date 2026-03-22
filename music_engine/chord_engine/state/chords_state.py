from enum import Enum


class ChordButton(Enum):
    SOUTH = "south"
    WEST = "west"
    NORTH = "north"
    EAST = "east"

class ChordsState:

    root_class: int
    note_classes: list[int]
    playing_notes: list[int]
    is_playing: bool
    active_button: ChordButton
    button_queue: list[ChordButton]

    def __init__(self) -> None:
        self.root_class = 0
        self.note_classes = []
        self.playing_notes = []
        self.is_playing = False
        self.active_button = ChordButton.SOUTH
        self.button_queue = []
