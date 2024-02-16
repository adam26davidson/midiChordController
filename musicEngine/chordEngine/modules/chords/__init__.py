from constants import BASS_CENTER, VOICING_PATTERNS, SPREAD_STEPS_PER_OCTAVE, \
    CENTER_NOTE
from ...utils import findAllOctavesInRange, findClosestNote
from ...chordEngineState import state

DEFAULT_SCALE = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]


class Chord:

    def __init__(self, chord, bass, root, scale=DEFAULT_SCALE):
        self.scale = scale
        self.root = root
        self.chord = chord
        self.bass = bass

        self.rootNotes = self.__findRootNotes()
        self.notes, self.allNotes = self.findAllNotes(self.chord)
        self.bassNotes, self.allBassNotes = self.findAllNotes(self.bass)
        self.bassRoots, self.allBassRoots = self.findAllNotes([self.bass[0]])

    def getChord(self):
        allNotes = self.__getAllNotes(state.key.value)
        chord = self.getChordFromNotes(allNotes)
        return chord

    def getRoot(self):
        return self.rootNotes[state.key.value]

    def getNoteTypes(self):
        return self.__getNotes(state.key.value)

    def getBass(self):
        allNotes = self.__getAllBassNotes(state.key.value)
        allRoots = self.__getAllBassRoots(state.key.value)
        bass = self.getBassFromNotes(allNotes, allRoots)
        return bass

    def getNoteForKey(self, note, key):
        index = (note + self.root) % len(self.scale)
        return (self.scale[index] + key) % 12

    def __findRootNotes(self):
        rootNotes = {}
        for key in range(0, 12):
            rootNotes[key] = (self.scale[self.root] + key) % 12
        return rootNotes

    def findAllNotes(self, noteDegrees):
        notes = {}
        allNotes = {}
        for key in range(0, 12):
            keyNotes = []
            for note in noteDegrees:
                keyNotes.append(self.getNoteForKey(note, key))
                keyNotes.sort()
            notes[key] = keyNotes
            allNotes[key] = findAllOctavesInRange(keyNotes)
        return notes, allNotes

    def __convertSpread(spread, chordLength):
        spreadsPerOct = chordLength - 1
        spreadOctaves = (spread * (1 / SPREAD_STEPS_PER_OCTAVE)) - 1
        return int(spreadOctaves*spreadsPerOct)

    def __getChordPattern(self, numNotes, voiceCount, spread):
        print("voiceCount: ", voiceCount)
        pattern = [0]
        if (voiceCount > 1):
            voiceCountPatterns = VOICING_PATTERNS[str(
                numNotes)][str(voiceCount)]
            maxSpread = len(voiceCountPatterns) - 1
            newSpread = min(spread, maxSpread)
            pattern = voiceCountPatterns[newSpread]
        return pattern

    def __getPatternParams(self):
        numNotes = len(self.chord)
        voiceCount = state.voiceCount

        # if voiceCount > numNotes:
        #     voiceCount = numNotes
        voiceCountDiff = voiceCount - numNotes
        spread = 0
        if voiceCount > numNotes:
            spread = Chord.__convertSpread(state.spread, numNotes + 1)
        else:
            spread = Chord.__convertSpread(state.spread, numNotes)
        voiceCount = numNotes + min(spread, voiceCountDiff)
        spread -= (voiceCount - numNotes)
        return numNotes, voiceCount, spread

    def __getChordFromPattern(self, pattern, allNotes):
        spreadSemitones = (state.spread / SPREAD_STEPS_PER_OCTAVE) * 12
        middleBottomNoteTarget = int(CENTER_NOTE - (spreadSemitones / 2))
        middleBottomNoteIndex = findClosestNote(
            middleBottomNoteTarget, allNotes)
        bottomNoteIndex = middleBottomNoteIndex + state.inversion.value
        bottomNoteIndex = max(0, bottomNoteIndex)
        topNoteIndex = pattern[len(pattern) - 1] + bottomNoteIndex
        if (topNoteIndex > (len(allNotes) - 1)):
            bottomNoteIndex -= topNoteIndex - (len(allNotes) - 1)
            topNoteIndex = (len(allNotes) - 1)
        chord = []
        for noteOffset in pattern:
            noteIndex = bottomNoteIndex + noteOffset
            chord.append(allNotes[noteIndex])
        return chord

    def getChordFromNotes(self, allNotes):
        params = self.__getPatternParams()
        pattern = self.__getChordPattern(*params)
        chord = self.__getChordFromPattern(pattern, allNotes)
        return chord

    def getBassFromNotes(self, allNotes, allRoots):
        centerIndexInRoots = findClosestNote(BASS_CENTER, allRoots)
        centerNote = allRoots[centerIndexInRoots]
        centerIndex = findClosestNote(centerNote, allNotes)
        index = centerIndex + state.bassPosition.value
        maxIndex = len(allNotes) - 1
        index = max(min(index, maxIndex), 0)
        return allNotes[index]

    def __getNotes(self, key):
        return self.notes[key]

    def __getAllNotes(self, key):
        return self.allNotes[key]

    def __getAllBassNotes(self, key):
        return self.allBassNotes[key]

    def __getAllBassRoots(self, key):
        return self.allBassRoots[key]
