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

    def getChord(self, state):
        chord = self.__getChordObject(state)
        return chord.getChord(state)

    def getBass(self, state):
        chord = self.__getChordObject(state)
        return chord.getBass(state)

    def getNoteTypes(self, state):
        chord = self.__getChordObject(state)
        return chord.getNoteTypes(state)

    def getRoot(self, state):
        return self.main.getRoot(state)

    def __getChordObject(self, state):
        if state['alternate']:
            return self.alternate
        else:
            return self.main
