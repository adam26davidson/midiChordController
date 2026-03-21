from ....modules.chords import DEFAULT_SCALE, Chord


class Secondary(Chord):

    def __init__(self, chord, bass, interval, scale=DEFAULT_SCALE):
        self.scale = scale
        self.interval = interval
        self.chord = chord
        self.bass = bass

        self.notes, self.allNotes = self.findAllNotes(self.chord)
        self.bassNotes, self.allBassNotes = self.findAllNotes(self.bass)
        self.bassRoots, self.allBassRoots = self.findAllNotes([self.bass[0]])

    def getChord(self, targetRoot):
        allNotes = self.__getAllNotes(targetRoot)
        chord = self.getChordFromNotes(allNotes)
        return chord

    def getBass(self, targetRoot):
        allNotes = self.__getAllBassNotes(targetRoot)
        allRoots = self.__getAllBassRoots(targetRoot)
        bass = self.getBassFromNotes(allNotes, allRoots)
        return bass

    def getRoot(self, targetRoot):
        return (targetRoot + self.interval) % 12

    def getNoteTypes(self, targetRoot):
        return self.__getNotes(targetRoot)

    def getNoteForKey(self, note, key):
        return (note + key) % 12

    def __getNotes(self, targetRoot):
        return self.notes[self.getRoot(targetRoot)]

    def __getAllNotes(self, targetRoot):
        return self.allNotes[self.getRoot(targetRoot)]

    def __getAllBassNotes(self, targetRoot):
        return self.allBassNotes[self.getRoot(targetRoot)]

    def __getAllBassRoots(self, targetRoot):
        return self.allBassRoots[self.getRoot(targetRoot)]
