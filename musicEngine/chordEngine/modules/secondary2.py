from .chord2 import Chord, DEFAULT_SCALE


class Secondary(Chord):
    def __init__(self, chord, bass, interval, scale=DEFAULT_SCALE):
        self.scale = scale
        self.interval = interval
        self.chord = chord
        self.bass = bass

        self.notes, self.allNotes = self.findAllNotes(self.chord)
        self.bassNotes, self.allBassNotes = self.findAllNotes(self.bass)
        self.bassRoots, self.allBassRoots = self.findAllNotes([self.bass[0]])

    def getChord(self, state, targetRoot):
        allNotes = self.__getAllNotes(targetRoot)
        chord = self.__getChordFromNotes(state, allNotes)
        return chord

    def getBass(self, state, targetRoot):
        allNotes = self.__getAllBassNotes(targetRoot)
        allRoots = self.__getAllBassRoots(targetRoot)
        bass = self.__getBassFromNotes(state, allNotes, allRoots)
        return bass

    def getRoot(self, state, targetRoot):
        return (targetRoot + self.interval) % 12

    def getNoteTypes(self, state, targetRoot):
        return self.__getNotes(targetRoot)

    def getNoteForKey(self, note, key):
        return (note + key) % 12

    def __getNotes(self, targetRoot):
        return self.notes[self.getRoot(None, targetRoot)]

    def __getAllNotes(self, targetRoot):
        return self.notes[self.getRoot(None, targetRoot)]

    def __getAllBassNotes(self, targetRoot):
        return self.allBassNotes[self.getRoot(None, targetRoot)]

    def __getAllBassRoots(self, targetRoot):
        return self.allBassRoots[self.getRoot(None, targetRoot)]
