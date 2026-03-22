

class ScaleState:

    key_agnostic: list[int]
    note_class_map: dict[int, list[int]]
    all_notes_map: dict[int, list[int]]

    def __init__(self) -> None:
        self.key_agnostic = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        self.note_class_map = {}
        self.all_notes_map = {}
