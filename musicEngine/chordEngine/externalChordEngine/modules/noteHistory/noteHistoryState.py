from typing import Dict, List

from musicEngine.chordEngine.externalChordEngine.modules.noteHistory import NoteHistory, NoteHistoryEvent


class NoteHistoryState():
    classesPlayed: List[int]
    lastContiguous: List[int]
    lastContiguousClasses: List[int]
    classRecencyRanking: List[int]
    lowestInContiguousClasses: int

    all: Dict[int, List[NoteHistoryEvent]] = {}

    memoryLength: float = 120.0
    