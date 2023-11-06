from typing import Dict, List


class NoteHistoryEvent():
    OnTime: int
    OffTime: int

    def __init__(self, OnTime: int, OffTime: int):
        self.OnTime = OnTime
        self.OffTime = OffTime


class NoteHistoryState():
    classesPlayed: List[int]
    lastContiguous: List[int]
    lastContiguousClasses: List[int]
    classRecencyRanking: List[int]
    lowestInContiguousClasses: int

    all: Dict[int, List[NoteHistoryEvent]] = {}

    memoryLength: float = 120.0
    