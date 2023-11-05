from typing import List
from enum import Enum


class ChordButton(Enum):
    SOUTH = "south"
    WEST = "west"
    NORTH = "north"
    EAST = "east"

class ChordsState():

    rootClass: int = 0
    NoteClasses: List[int] = []
    playingNotes: List[int] = []
    isPlaying: bool = False
    activeButton: ChordButton = ChordButton.SOUTH
    buttonQueue: List[int] = []
