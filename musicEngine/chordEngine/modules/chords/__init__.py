from constants import BASS_CENTER, CENTER_NOTE, SPREAD_STEPS_PER_OCTAVE, VOICING_PATTERNS

from ...chordEngineState import state
from ...utils import find_all_octaves_in_range, find_closest_note

DEFAULT_SCALE = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]


class Chord:

    def __init__(self, chord, bass, root, scale=DEFAULT_SCALE):
        self.scale = scale
        self.root = root
        self.chord = chord
        self.bass = bass

        self.root_notes = self.__find_root_notes()
        self.notes, self.all_notes = self.find_all_notes(self.chord)
        self.bass_notes, self.all_bass_notes = self.find_all_notes(self.bass)
        self.bass_roots, self.all_bass_roots = self.find_all_notes([self.bass[0]])

    def get_chord(self):
        all_notes = self.__get_all_notes(state.key.value)
        chord = self.get_chord_from_notes(all_notes)
        return chord

    def get_root(self):
        return self.root_notes[state.key.value]

    def get_note_types(self):
        return self.__get_notes(state.key.value)

    def get_bass(self):
        all_notes = self.__get_all_bass_notes(state.key.value)
        all_roots = self.__get_all_bass_roots(state.key.value)
        bass = self.get_bass_from_notes(all_notes, all_roots)
        return bass

    def get_note_for_key(self, note, key):
        index = (note + self.root) % len(self.scale)
        return (self.scale[index] + key) % 12

    def __find_root_notes(self):
        root_notes = {}
        for key in range(12):
            root_notes[key] = (self.scale[self.root] + key) % 12
        return root_notes

    def find_all_notes(self, note_degrees):
        notes = {}
        all_notes = {}
        for key in range(12):
            key_notes = []
            for note in note_degrees:
                key_notes.append(self.get_note_for_key(note, key))
                key_notes.sort()
            notes[key] = key_notes
            all_notes[key] = find_all_octaves_in_range(key_notes)
        return notes, all_notes

    def __convert_spread(self, spread, chord_length):
        spreads_per_oct = chord_length - 1
        spread_octaves = (spread * (1 / SPREAD_STEPS_PER_OCTAVE)) - 1
        return int(spread_octaves*spreads_per_oct)

    def __get_chord_pattern(self, num_notes, voice_count, spread):
        pattern = [0]
        if (voice_count > 1):
            voice_count_patterns = VOICING_PATTERNS[str(
                num_notes)][str(voice_count)]
            max_spread = len(voice_count_patterns) - 1
            new_spread = min(spread, max_spread)
            pattern = voice_count_patterns[new_spread]
        return pattern

    def __get_pattern_params(self):
        num_notes = len(self.chord)
        voice_count = state.voice_count
        voice_count_diff = voice_count - num_notes
        spread = 0
        if voice_count > num_notes:
            spread = Chord.__convert_spread(state.spread, num_notes + 1)
        else:
            spread = Chord.__convert_spread(state.spread, num_notes)
        voice_count = num_notes + min(spread, voice_count_diff)
        spread -= (voice_count - num_notes)
        return num_notes, voice_count, spread

    def __get_chord_from_pattern(self, pattern, all_notes):
        spread_semitones = (state.spread / SPREAD_STEPS_PER_OCTAVE) * 12
        middle_bottom_note_target = int(CENTER_NOTE - (spread_semitones / 2))
        middle_bottom_note_index = find_closest_note(
            middle_bottom_note_target, all_notes)
        bottom_note_index = middle_bottom_note_index + state.inversion.value
        bottom_note_index = max(0, bottom_note_index)
        top_note_index = pattern[len(pattern) - 1] + bottom_note_index
        if (top_note_index > (len(all_notes) - 1)):
            bottom_note_index -= top_note_index - (len(all_notes) - 1)
            top_note_index = (len(all_notes) - 1)
        chord = []
        for note_offset in pattern:
            note_index = bottom_note_index + note_offset
            chord.append(all_notes[note_index])
        return chord

    def get_chord_from_notes(self, all_notes):
        params = self.__get_pattern_params()
        pattern = self.__get_chord_pattern(*params)
        chord = self.__get_chord_from_pattern(pattern, all_notes)
        return chord

    def get_bass_from_notes(self, all_notes, all_roots):
        center_index_in_roots = find_closest_note(BASS_CENTER, all_roots)
        center_note = all_roots[center_index_in_roots]
        center_index = find_closest_note(center_note, all_notes)
        index = center_index + state.bass_position.value
        max_index = len(all_notes) - 1
        index = max(min(index, max_index), 0)
        return all_notes[index]

    def __get_notes(self, key):
        return self.notes[key]

    def __get_all_notes(self, key):
        return self.all_notes[key]

    def __get_all_bass_notes(self, key):
        return self.all_bass_notes[key]

    def __get_all_bass_roots(self, key):
        return self.all_bass_roots[key]
