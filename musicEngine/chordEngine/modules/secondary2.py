from .chord2 import Chord, DEFAULT_SCALE


class Secondary(Chord):
    def __init__(self, chord, bass, interval, scale=DEFAULT_SCALE):
        self.scale = scale
        self.interval = interval
        self.chord = chord
        self.bass = bass

        self.notes, self.allNotes = self.findNotes(self.chord)
        self.bassNotes, self.allBassNotes, \
            self.bassRoots = self.__findBassNotes(self.bass)

    def getChord(self, state, targetRoot):
        allNotes = self.__getAllNotes(targetRoot)
        chord = self.__getChordFromNotes(state, allNotes)
        return chord

    def getRoot(self, targetRoot):
        return (targetRoot + self.interval) % 12

    def getNoteTypes(self, targetRoot):
        return self.__getNotes(targetRoot)

    def getBass(self, state, targetRoot):
        allNotes = self.__getAllBassNotes(targetRoot)
        allRoots = self.__getBassRoots(targetRoot)
        bass = self.__getBassFromNotes(state, allNotes, allRoots)
        return bass

    def __getNotes(self, targetRoot):
        return self.notes[self.getRoot(targetRoot)]

    def __getAllNotes(self, targetRoot):
        return self.notes[self.getRoot(targetRoot)]

    def __getAllBassNotes(self, targetRoot):
        return self.allBassNotes[self.getRoot(targetRoot)]

    def __getBassRoots(self, targetRoot):
        return self.bassRoots[self.getRoot(targetRoot)]
