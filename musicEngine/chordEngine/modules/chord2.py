from constants import BASS_CENTER, VOICING_PATTERNS, SPREAD_STEPS_PER_OCTAVE, \
    CENTER_NOTE
from utils import findAllOctavesInRange, findClosestNote

DEFAULT_SCALE = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]


class Chord:
    def init(self):
        pass

    def __init__(self, chord, bass, root, scale=DEFAULT_SCALE):
        self.scale = scale
        self.root = root
        self.chord = chord
        self.bass = bass

        self.rootNotes = self.__findRootNotes()
        self.notes, self.allNotes = self.findNotes(self.chord)
        self.bassNotes, self.allBassNotes, \
            self.bassRoots = self.__findBassNotes(self.bass)

    def getChord(self, state):
        allNotes = self.__getAllNotes(state['key'])
        chord = self.__getChordFromNotes(state, allNotes)
        return chord

    def getRoot(self, key):
        return self.rootNotes[key]

    def getNoteTypes(self, state):
        return self.__getNotes(state['key'])

    def getBass(self, state):
        allNotes = self.__getAllBassNotes(state['key'])
        allRoots = self.__getBassRoots(state['key'])
        bass = self.__getBassFromNotes(state, allNotes, allRoots)
        return bass

    def __findRootNotes(self):
        rootNotes = {}
        for key in range(0, 12):
            rootNotes[key] = (self.scale[self.root] + key) % 12
        return rootNotes

    def findNotes(self, chord):
        notes = {}
        allNotes = {}
        for key in range(0, 12):
            keyNotes = []
            for note in chord:
                index = (note + self.root) % len(self.scale)
                keyNotes.append((self.scale[index] + key) % 12)
                keyNotes.sort()
            notes[key] = keyNotes
            allNotes[key] = findAllOctavesInRange(keyNotes)
        return notes, allNotes

    def __findBassNotes(self, degrees):
        roots = {}
        for key in range(0, 12):
            index = (degrees[0] + self.root) % len(self.scale)
            roots[key] = (self.scale[index] + key) % 12
        notes, allNotes = self.__findNotes(degrees)
        return notes, allNotes, roots

    def __convertSpread(spread, chordLength):
        spreadsPerOct = chordLength - 1
        spreadOctaves = (spread * (1 / SPREAD_STEPS_PER_OCTAVE)) - 1
        return int(spreadOctaves*spreadsPerOct)

    def __getChordPattern(self, numNotes, voiceCount, spread):
        pattern = [0]
        if (voiceCount > 1):
            voiceCountPatterns = VOICING_PATTERNS[str(
                numNotes)][str(voiceCount)]
            maxSpread = len(voiceCountPatterns) - 1
            newSpread = min(spread, maxSpread)
            pattern = voiceCountPatterns[newSpread]
        return pattern

    def __getPatternParams(self, state):
        numNotes = len(self.chord)
        voiceCount = state["voiceCount"]
        if state["voiceCountMode"] == "max" and voiceCount > numNotes:
            voiceCount = numNotes
        voiceCountDiff = voiceCount - numNotes
        spread = 0
        if voiceCount > numNotes:
            spread = Chord.__convertSpread(state["spread"], numNotes + 1)
        else:
            spread = Chord.__convertSpread(state["spread"], numNotes)
        voiceCount = numNotes + min(spread, voiceCountDiff)
        spread -= (voiceCount - numNotes)
        return numNotes, voiceCount, spread

    def __getChordFromPattern(self, state, pattern, allNotes):
        spreadSemitones = (state["spread"] / SPREAD_STEPS_PER_OCTAVE) * 12
        middleBottomNoteTarget = int(CENTER_NOTE - (spreadSemitones / 2))
        middleBottomNoteIndex = findClosestNote(
            middleBottomNoteTarget, allNotes)
        bottomNoteIndex = middleBottomNoteIndex + state["inversion"]
        bottomNoteIndex = max(0, bottomNoteIndex)
        topNoteIndex = pattern[len(pattern) - 1] + bottomNoteIndex
        if (topNoteIndex > (len(allNotes) - 1)):
            bottomNoteIndex -= topNoteIndex - (len(allNotes) - 1)
            topNoteIndex = (len(allNotes) - 1)
        chord = []
        for noteOffset in pattern:
            noteIndex = bottomNoteIndex + noteOffset
            chord.append(self.allNotes[noteIndex])
        return chord

    def __getChordFromNotes(self, state, allNotes):
        params = self.__getPatternParams(state)
        pattern = self.__getChordPattern(*params)
        chord = self.__getChordFromPattern(state, pattern, allNotes)
        return chord

    def __getBassFromNotes(self, state, allNotes, allRoots):
        centerIndexInRoots = findClosestNote(BASS_CENTER, allRoots)
        centerNote = allRoots[centerIndexInRoots]
        centerIndex = findClosestNote(centerNote, allNotes)
        index = centerIndex + state['bassPosition']
        maxIndex = len(allNotes) - 1
        index = max(min(index, maxIndex), 0)
        return allNotes[index]

    def __getNotes(self, key):
        return self.notes[key]

    def __getAllNotes(self, key):
        return self.notes[key]

    def __getAllBassNotes(self, key):
        return self.allBassNotes[key]

    def __getBassRoots(self, key):
        return self.bassRoots[key]
