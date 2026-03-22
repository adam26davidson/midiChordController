from __future__ import annotations

from constants import MAX_NOTE, MIN_NOTE


# find all octaves of the specified array of notes
def find_all_octaves_in_range(notes: list[int], min: int = MIN_NOTE, max: int = MAX_NOTE) -> list[int]:
    completed_notes: list[int] = []
    midi_notes: list[int] = []
    for note in notes:
        # ensure no duplicates
        if completed_notes.count(note) == 0:
            for i in range(min, max + 1):
                if i % 12 == note:
                    midi_notes.append(i)
            completed_notes.append(note)
    midi_notes.sort()
    return midi_notes


def find_closest_note(target_note: int, sorted_notes: list[int]) -> int:
    upper_index = 0
    for index in range(len(sorted_notes)):
        if sorted_notes[index] > target_note:
            upper_index = index
            break
        if (index == len(sorted_notes) - 1):
            return index
    if (upper_index == 0):
        return 0
    upper_distance = abs(sorted_notes[upper_index] - target_note)
    lower_distance = abs(sorted_notes[upper_index - 1] - target_note)
    if upper_distance < lower_distance:
        return upper_index
    return upper_index - 1
