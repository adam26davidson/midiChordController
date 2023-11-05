
from enum import Enum
from typing import List


class ChordEngineMessageType(Enum):
    ON = 1
    OFF = 2

class ChordPlayer(Enum):
    BASS = 1
    CHORD = 2

class ChordEngineMessage():
    type: ChordEngineMessageType
    notes: List[int]
    player: ChordPlayer