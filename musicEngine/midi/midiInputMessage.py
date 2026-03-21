
from enum import Enum


class MidiInputMessageType(Enum):
    NOTE_ON = 0
    NOTE_OFF = 1

class MidiInputMessage:
    type: MidiInputMessageType
    note: int

    def __init__(self, type: MidiInputMessageType, note: int):
        self.type = type
        self.note = note
