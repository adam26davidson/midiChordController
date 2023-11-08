from typing import Dict, List


class NoteHistoryEvent():
    OnTime: int
    OffTime: int

    def __init__(self, OnTime: int, OffTime: int):
        self.OnTime = OnTime
        self.OffTime = OffTime


class NoteHistoryState():
    notesPlayed: List[int] = []
    classesPlayed: List[int] = []
    lastContiguous: List[int] = []
    lastContiguousClasses: List[int] = []
    classRecencyRanking: List[int] = []
    lowestInContiguousClasses: int = 127

    all: Dict[int, List[NoteHistoryEvent]] = {}

    memoryLength: float = 120.0
    