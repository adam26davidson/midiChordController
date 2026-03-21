from ....modules.chords import DEFAULT_SCALE, Chord


class Secondary(Chord):

    def __init__(self, chord, bass, interval, scale=DEFAULT_SCALE):
        self.scale = scale
        self.interval = interval
        self.chord = chord
        self.bass = bass

        self.notes, self.all_notes = self.find_all_notes(self.chord)
        self.bass_notes, self.all_bass_notes = self.find_all_notes(self.bass)
        self.bass_roots, self.all_bass_roots = self.find_all_notes([self.bass[0]])

    def get_chord(self, target_root):
        all_notes = self.__get_all_notes(target_root)
        chord = self.get_chord_from_notes(all_notes)
        return chord

    def get_bass(self, target_root):
        all_notes = self.__get_all_bass_notes(target_root)
        all_roots = self.__get_all_bass_roots(target_root)
        bass = self.get_bass_from_notes(all_notes, all_roots)
        return bass

    def get_root(self, target_root):
        return (target_root + self.interval) % 12

    def get_note_types(self, target_root):
        return self.__get_notes(target_root)

    def get_note_for_key(self, note, key):
        return (note + key) % 12

    def __get_notes(self, target_root):
        return self.notes[self.get_root(target_root)]

    def __get_all_notes(self, target_root):
        return self.all_notes[self.get_root(target_root)]

    def __get_all_bass_notes(self, target_root):
        return self.all_bass_notes[self.get_root(target_root)]

    def __get_all_bass_roots(self, target_root):
        return self.all_bass_roots[self.get_root(target_root)]
