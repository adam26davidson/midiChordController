from ...chordEngineState import state
from ...internalChordEngine.modules.secondaries.secondary import Secondary
from . import DEFAULT_SCALE, Chord


class DualChord:

    def __init__(self, setting, scale=DEFAULT_SCALE, is_secondary=False):
        chord_class = Secondary if is_secondary else Chord
        root_or_interval = setting['interval'] if is_secondary \
            else setting['root']
        self.main = chord_class(
            setting['main'],
            setting['mainBass'],
            root_or_interval, scale
        )
        self.alternate = chord_class(
            setting['alternate'],
            setting['alternateBass'],
            root_or_interval, scale
        )

    def get_chord(self, target_note=None):
        chord, args = self.__get_chord_object(target_note)
        return chord.get_chord(*args)

    def get_bass(self, target_note=None):
        chord, args = self.__get_chord_object(target_note)
        return chord.get_bass(*args)

    def get_note_types(self, target_note=None):
        chord, args = self.__get_chord_object(target_note)
        return chord.get_note_types(*args)

    def get_root(self, target_note=None):
        chord, args = self.__get_chord_object(target_note)
        return chord.get_root(*args)

    def __get_chord_object(self, target_note):
        args = [] if target_note is None else [target_note]
        if state.alternate:
            return self.alternate, args
        return self.main, args
