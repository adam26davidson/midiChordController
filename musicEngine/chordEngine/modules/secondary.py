from .chord import Chord
from constants import VOICING_PATTERNS, CENTER_NOTE, SPREAD_STEPS_PER_OCTAVE


def parseSecondaries(settings):
    def parseSecondary(setting):
        secondaries = {}
        default = Secondary(setting)
        buttons = ["south", "west", "north", "east"]

        def getOverrideSecondary(overides):
            overideSettings = setting.copy()
            for key in overides:
                overideSettings[key] = overides[key]
            return Secondary(overideSettings)

        for button in buttons:
            if not (button in setting):
                secondaries[button] = {
                    "default": default,
                    "leftModulation": default,
                    "rightModulation": default
                }
            else:
                secondaries[button] = {}
                for key in "default", "leftModulation", "rightModulation":
                    if key in setting[button]:
                        secondaries[button][key] = getOverrideSecondary(
                            setting[button][key])
                    else:
                        secondaries[button][key] = default
        return secondaries

    left = parseSecondary(settings["left"])
    right = parseSecondary(settings["right"])
    return {"left": left, "right": right}


class Secondary():
    def __init__(self, setting):
        self.interval = setting["interval"]
        self.main = setting["main"]
        self.mainBass = setting["mainBass"]
        self.alt = setting["alternate"]
        self.altBass = setting["alternateBass"]

        # find actual notes and all midi notes for each key
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

    def findNotes(self, chord):
        notes = {}
        allNotes = {}
        for key in range(0, 12):
            notes[key] = []
            for note in chord:
                notes[key].append((note + key) % 12)
            notes[key].sort()
            allNotes[key] = Chord.findAllNotes(notes[key])
        return notes, allNotes

    def findBassNotes(self, notes):
        roots = {}
        for key in range(0, 12):
            roots[key] = (notes[0] + key) % 12
        notes, allNotes = self.findNotes(notes)
        return notes, allNotes, roots

    def getBassFromParams(self, state, key, params, allNotes):
        root = (key + self.interval) % 12
        p = state['bassPosition']
        if p <= params[root]["topCount"] and p >= (-1*params[root]["bottomCount"]):
            return allNotes[root][params[root]["center"] + p]
        elif p > params[root]["topCount"]:
            return allNotes[root][len(allNotes[root]) - 1]
        elif p < (-1*params[root]["bottomCount"]):
            return allNotes[root][0]

    def getChordFromParams(self, state, key, inversionParams, voicings):
        root = (key + self.interval) % 12
        spread = Chord.convertSpread(
            state['spread'], len(voicings[root][0][0]))
        if spread >= len(voicings[root]):
            spread = len(voicings[root]) - 1
        params = inversionParams[root][spread]
        # if the inversion is within range
        if state['inversion'] <= params["topCount"] and state['inversion'] >= (-1*params["bottomCount"]):
            return voicings[root][spread][params["center"] + state['inversion']]
        # if the inversion is above the range
        elif state['inversion'] > params["topCount"]:
            # if upper limit is not exceeded by more than the spread
            if state['inversion'] - params["topCount"] < spread:
                spreadVoicings = voicings[root][spread -
                                                (state['inversion'] - params["topCount"])]
                return spreadVoicings[len(spreadVoicings)-1]
            # if upper limit is exceeded by more than the spread
            else:
                return voicings[root][0][len(voicings[root][0]) - 1]
        # if the inversion is below the lower limit
        elif state['inversion'] < (-1*params["bottomCount"]):
            # if lower limit is not exceeded by more than the spread
            if state['inversion'] + params["bottomCount"] < spread:
                spreadVoicings = voicings[root][spread -
                                                (state['inversion'] + params["bottomCount"])]
                return spreadVoicings[0]
            # if the limit range is exceeded by more than the spread
            else:
                return voicings[root][0][0]

    def __getChordNotes(self, state, noteTypes, allNotes):
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
        return (key + self.interval) % 12

    def getNoteTypes(self, state, key):
        root = self.getRoot(key)
        if state['alternate']:
            return self.altNotes[root]
        else:
            return self.mainNotes[root]

    def getChord(self, state, key):
        root = (key + self.interval) % 12
        if state['alternate']:
            return self.__getChordNotes(state, self.altNotes[root],
                                        self.allAltNotes[root])
        else:
            return self.__getChordNotes(state, self.mainNotes[root],
                                        self.allMainNotes[root])

    def getBass(self, state, key):
        if state['alternate']:
            return self.getBassFromParams(state, key, self.altBassParams, self.allAltBassNotes)
        else:
            return self.getBassFromParams(state, key, self.mainBassParams, self.allMainBassNotes)
