from __future__ import annotations


class Modulation:

    def __init__(self, scale: list[int], setting: dict) -> None:
        self.scale = scale
        if setting["type"] == "modal":
            self.map = self.find_modal_map(setting["map"])
        else:
            self.map = setting["map"]
        self.offsets = self.find_offsets()

    def find_modal_map(self, map: list[int]) -> list[int]:
        scale_pattern: list[bool] = []  # will be something like [T,F,T,F,T,T,F,T,F,T,F,T]
        for i in range(12):
            if (self.scale.count(i) == 0):
                scale_pattern.append(False)
            else:
                scale_pattern.append(True)
        cycles = ((self.scale[map[0]] - self.scale[map[1]]) + 12) % 12
        for _ in range(cycles):
            val = scale_pattern.pop(0)
            scale_pattern.append(val)
        explicit_map: list[int] = []
        for i in range(12):
            if scale_pattern[i]:
                explicit_map.append(i)
        return explicit_map

    def find_offsets(self) -> list[int]:
        offsets: list[int] = []
        for i in range(len(self.scale)):
            offsets.append(self.map[i] - self.scale[i])
        return offsets

    def apply(self, notes: list[int], scale: list[int]) -> list[int]:
        mod_notes: list[int] = []
        for note in notes:
            mod_notes.append(self.apply_one(note, scale))
        return mod_notes

    def apply_one(self, note: int, scale: list[int]) -> int:
        index = scale.index(note % 12)
        return note + self.offsets[index]

    def apply_to_scale(self) -> list[int]:
        new_scale: list[int] = []
        for i in range(len(self.scale)):
            new_scale.append((self.scale[i] + self.offsets[i]) % 12)
        return new_scale
