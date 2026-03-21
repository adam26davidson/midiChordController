

class NoteHistoryEvent:
    OnTime: int
    OffTime: int

    def __init__(self, OnTime: int, OffTime: int):
        self.OnTime = OnTime
        self.OffTime = OffTime


class NoteHistoryState:
    lowestInContiguousClasses: int
    memoryLength: float

    def __init__(self):
        self.notesPlayed: list[int] = []
        self.classesPlayed: list[int] = []
        self.lastContiguous: list[int] = []
        self.lastContiguousClasses: list[int] = []
        self.classRecencyRanking: list[int] = []
        self.lowestInContiguousClasses = 127
        self.all: dict[int, list[NoteHistoryEvent]] = {}
        self.memoryLength = 120.0
