
from enum import Enum


class ChordMessageType(Enum):
    ON = 1
    OFF = 2

class ChordPlayer(Enum):
    BASS = 1
    CHORD = 2

class ChordEngineMessage:
    type: ChordMessageType
    notes: list[int]
    player: ChordPlayer

    def __init__(self, type: ChordMessageType, notes: list[int], player: ChordPlayer):
        self.type = type
        self.notes = notes
        self.player = player
