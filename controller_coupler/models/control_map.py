from __future__ import annotations


class ControlMap:
    name: str
    display_name: str
    inversion_mode: str
    bass_mode: str
    map: dict[str, list[str]]

    def __init__(self, name: str, display_name: str, inversion_mode: str, bass_mode: str, map: dict[str, list[str]]):
        self.name = name
        self.display_name = display_name
        self.inversion_mode = inversion_mode
        self.bass_mode = bass_mode
        self.map = map
