from enum import Enum


class ChordButton(Enum):
    SOUTH = "south"
    WEST = "west"
    NORTH = "north"
    EAST = "east"

class ChordsState:

    rootClass: int = 0
    NoteClasses: list[int] = []
    playingNotes: list[int] = []
    isPlaying: bool = False
    activeButton: ChordButton = ChordButton.SOUTH
    buttonQueue: list[int] = []
