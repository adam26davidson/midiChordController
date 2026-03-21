


class NoteHistoryEvent:
    on_time: int
    off_time: int

    def __init__(self, on_time: int, off_time: int):
        self.on_time = on_time
        self.off_time = off_time


class NoteHistoryState:
    lowest_in_contiguous_classes: int
    memory_length: float

    def __init__(self):
        self.notesPlayed: list[int] = []
        self.classesPlayed: list[int] = []
        self.lastContiguous: list[int] = []
        self.lastContiguousClasses: list[int] = []
        self.classRecencyRanking: list[int] = []
        self.lowest_in_contiguous_classes = 127
        self.all: dict[int, list[NoteHistoryEvent]] = {}
        self.memory_length = 120.0
