from .chord2 import Chord, DEFAULT_SCALE
from .secondary2 import Secondary


class DualChord:
    def __init__(self, setting, scale=DEFAULT_SCALE, isSecondary=False):
        ChordClass = Secondary if isSecondary else Chord
        rootOrInterval = setting['interval'] if isSecondary \
            else setting['root']
        self.main = ChordClass(
            setting['main'],
            setting['mainBass'],
            rootOrInterval, scale
        )
        self.alternate = ChordClass(
            setting['alternate'],
            setting['alternateBass'],
            rootOrInterval, scale
        )

    def getChord(self, state, targetNote=None):
        chord, args = self.__getChordObject(state, targetNote)
        return chord.getChord(*args)

    def getBass(self, state, targetNote=None):
        chord, args = self.__getChordObject(state, targetNote)
        return chord.getBass(*args)

    def getNoteTypes(self, state, targetNote=None):
        chord, args = self.__getChordObject(state, targetNote)
        return chord.getNoteTypes(*args)

    def getRoot(self, state, targetNote=None):
        chord, args = self.__getChordObject(state, targetNote)
        return chord.getRoot(*args)

    def __getChordObject(self, state, targetNote):
        args = (state) if targetNote is None else (state, targetNote)
        if state['alternate']:
            return self.alternate, args
        else:
            return self.main, args
