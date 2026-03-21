from ...chordEngineState import state
from ...internalChordEngine.modules.secondaries.secondary import Secondary
from . import DEFAULT_SCALE, Chord


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

    def getChord(self, targetNote=None):
        chord, args = self.__getChordObject(targetNote)
        return chord.getChord(*args)

    def getBass(self, targetNote=None):
        chord, args = self.__getChordObject(targetNote)
        return chord.getBass(*args)

    def getNoteTypes(self, targetNote=None):
        chord, args = self.__getChordObject(targetNote)
        return chord.getNoteTypes(*args)

    def getRoot(self, targetNote=None):
        chord, args = self.__getChordObject(targetNote)
        return chord.getRoot(*args)

    def __getChordObject(self, targetNote):
        args = [] if targetNote is None else [targetNote]
        if state.alternate:
            return self.alternate, args
        return self.main, args
