import json
import os
import itertools

PARENT_PATH = os.path.dirname(os.path.abspath(__file__))


class MidiChordFinder:
    def __init__(self, middleMidiNote, voicingPatterFileName):
        self.middleMidiNote = middleMidiNote
        voicingPatternParent = json.load(
            open(PARENT_PATH + voicingPatterFileName))
        self.voicingPatterns = voicingPatternParent["voicingPatterns"]
        self.maxNotes = voicingPatternParent["maxNotes"]
        self.maxVoiceCount = voicingPatternParent["maxVoiceCount"]
        self.maxOctaves = voicingPatternParent["maxOctaves"]
    
    def __findChords(self):
        allChords = {}
        noteOptions = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        for noteCount in range(1, self.maxNotes):
            combinations = itertools.combinations(noteOptions, noteCount)
            for combination in combinations:
                self.__findChord(list(combination))

    def __findChord(combination):
        for key in range(0, 12):

    def findNotes(self, chord):
        #set main chord notes
        notes = {}
        allNotes = {}
        for key in range(0, 12):
            keyNotes = []
            for note in chord:
                index = (note + self.root) % len(self.scale)
                keyNotes.append((self.scale[index] + key) % 12)
                keyNotes.sort()
            notes[key] = keyNotes # chord notes for key
            allNotes[key] = Chord.findAllNotes(keyNotes) # all octaves of chord notes for key
        return notes, allNotes

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
