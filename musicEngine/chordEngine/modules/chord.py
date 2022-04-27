from constants import VOICING_PATTERNS, SPREAD_STEPS_PER_OCTAVE, \
    CENTER_NOTE, MIN_NOTE, MAX_NOTE, BASS_OCTAVE_RANGE


class Chord:
    def __init__(self, scale, setting):

        self.scale = scale  # set scale for convenience
        self.root = setting["root"]  # index of the root in key agnostic scale

        # indices of chord notes in key agnostic scale
        self.main = setting["main"]
        # indices of alternate chord notes in key agnostic scale
        self.mainBass = setting["mainBass"]
        # indices of alternate chord notes in key agnostic scale
        self.alt = setting["alternate"]
        # indices of alternate chord notes in key agnostic scale
        self.altBass = setting["alternateBass"]

        self.rootNotes = self.findRootNotes()  # set root note for each key

        # find chord and bass notes for each key
        self.mainNotes, self.allMainNotes = self.findNotes(self.main)
        self.altNotes, self.allAltNotes = self.findNotes(self.alt)
        self.mainBassNotes, self.allMainBassNotes, self.mainBassRoots = self.findBassNotes(
            self.mainBass)
        self.altBassNotes, self.allAltBassNotes, self.altBassRoots = self.findBassNotes(
            self.altBass)

        # find the home inversion, number of top and bottom inversions
        self.mainBassParams = Chord.findBassParams(
            self.allMainBassNotes, self.mainBassRoots)
        self.altBassParams = Chord.findBassParams(
            self.allAltBassNotes, self.altBassRoots)

    # find all octaves of the specified array of notes
    def findAllNotes(notes, min=MIN_NOTE, max=MAX_NOTE):
        completedNotes = []
        midiNotes = []
        for note in notes:
            # ensure no duplicates
            if completedNotes.count(note) == 0:
                for i in range(min, max + 1):
                    if i % 12 == note:
                        midiNotes.append(i)
                completedNotes.append(note)
        midiNotes.sort()
        return midiNotes

    # set the root of the chord for each key
    def findRootNotes(self):
        rootNotes = {}
        for key in range(0, 12):
            rootNotes[key] = (self.scale[self.root] + key) % 12
        return rootNotes

    def findNotes(self, chord):
        # set main chord notes
        notes = {}
        allNotes = {}
        for key in range(0, 12):
            keyNotes = []
            for note in chord:
                index = (note + self.root) % len(self.scale)
                keyNotes.append((self.scale[index] + key) % 12)
                keyNotes.sort()
            notes[key] = keyNotes  # chord notes for key
            # all octaves of chord notes for key
            allNotes[key] = Chord.findAllNotes(keyNotes)
        return notes, allNotes

    def findBassNotes(self, degrees):
        roots = {}
        for key in range(0, 12):
            index = (degrees[0] + self.root) % len(self.scale)
            roots[key] = (self.scale[index] + key) % 12
        notes, allNotes = self.findNotes(degrees)
        return notes, allNotes, roots

    def findBassParams(allNotes, roots):
        params = {}
        for k in range(0, 12):
            params[k] = {}
            for n in range(0, len(allNotes[k])):
                inRange = allNotes[k][n] >= BASS_OCTAVE_RANGE["min"] \
                    and allNotes[k][n] <= BASS_OCTAVE_RANGE["max"]
                isRoot = allNotes[k][n] % 12 == roots[k]
                if inRange and isRoot:
                    params[k] = {
                        "center": n,
                        "topCount": (len(allNotes[k]) - n) - 1,
                        "bottomCount": n
                    }
                    break
        return params

    def convertSpread(spread, chordLength):
        spreadsPerOct = chordLength - 1
        spreadOctaves = (spread * (1 / SPREAD_STEPS_PER_OCTAVE)) - 1
        return int(spreadOctaves*spreadsPerOct)

    def getBassFromParams(self, state, params, allNotes):
        p = state['bassPosition']
        key = state['key']
        if p <= params[key]["topCount"] and p >= (-1*params[key]["bottomCount"]):
            return allNotes[key][params[key]["center"] + p]
        elif p > params[key]["topCount"]:
            return allNotes[key][len(allNotes[key]) - 1]
        elif p < (-1*params[key]["bottomCount"]):
            return allNotes[key][0]

    def findClosestNote(targetNote, allNotes):
        upperIndex = 0
        for index in range(0, len(allNotes)):
            if allNotes[index] > targetNote:
                upperIndex = index
                break
            elif (index == len(allNotes) - 1):
                return index
        if (upperIndex == 0):
            return 0
        upperDistance = abs(allNotes[upperIndex] - targetNote)
        lowerDistance = abs(allNotes[upperIndex - 1] - targetNote)
        if upperDistance < lowerDistance:
            return upperIndex
        else:
            return upperIndex - 1

    def __getChordNotes(state, noteTypes, allNotes):
        numNotes = len(noteTypes)
        voiceCount = state["voiceCount"]
        if state["voiceCountMode"] == "max" and voiceCount > numNotes:
            voiceCount = numNotes
        voiceCountDiff = voiceCount - numNotes
        spread = 0
        if voiceCount > numNotes:
            spread = Chord.convertSpread(state["spread"], numNotes + 1)
            voiceCount = numNotes + min(spread, voiceCountDiff)
        else:
            spread = Chord.convertSpread(state["spread"], numNotes)
        spread -= (voiceCount - numNotes)
        pattern = [0]
        if (voiceCount > 1):
            voiceCountPatterns = VOICING_PATTERNS[str(
                numNotes)][str(voiceCount)]
            maxSpread = len(voiceCountPatterns) - 1
            spread = min(spread, maxSpread)
            pattern = voiceCountPatterns[spread]
        spreadSemitones = (state["spread"] / SPREAD_STEPS_PER_OCTAVE) * 12
        middleBottomNoteTarget = int(CENTER_NOTE - (spreadSemitones / 2))
        middleBottomNoteIndex = Chord.findClosestNote(
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
            chord.append(allNotes[noteIndex])
        return chord

    def getRoot(self, key):
        (key + self.interval) % 12 if self.secondary else self.rootNotes[key]

    def getNoteTypes(self, state):
        if state['alternate']:
            return self.altNotes[state['key']]
        else:
            return self.mainNotes[state['key']]

    def getChord(self, state):
        if state['alternate']:
            return Chord.__getChordNotes(state, self.altNotes[state['key']],
                                         self.allAltNotes[state['key']])
        else:
            return Chord.__getChordNotes(state, self.mainNotes[state['key']],
                                         self.allMainNotes[state['key']])

    def getBass(self, state):
        if state['alternate']:
            return self.getBassFromParams(state, self.altBassParams,
                                          self.allAltBassNotes)
        else:
            return self.getBassFromParams(state, self.mainBassParams,
                                          self.allMainBassNotes)
