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
        if state['alternate']:
            return self.alternate.getChord(state)
        else:
            return self.main.getChord(state)

    def getBass(self, state):
        if state['alternate']:
            return self.alternate.getBass(state)
        else:
            return self.main.getBass(state)

    def getNoteTypes(self, state):
        if state['alternate']:
            return self.alternate.getNoteTypes(state)
        else:
            return self.main.getNoteTypes(state)

    def getRoot(self, state):
        return self.main.getRoot(state)
