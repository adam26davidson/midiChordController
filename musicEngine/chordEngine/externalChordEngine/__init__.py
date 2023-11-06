import time
from typing import List, Tuple
from models.appParameter import AppParameterType
from musicEngine.chordEngine.chordEngine import ChordEngine
from musicEngine.chordEngine.externalChordEngine.modules.noteHistory import NoteHistory
from musicEngine.chordEngine.modules.chords import Chord
from musicEngine.chordEngine.state.chordsState import ChordButton
from musicEngine.midi.midiInputMessage import MidiInputMessage, MidiInputMessageType
from ..chordEngineState import ExternalChordMode, ExternalChordScaleMode, state


class ExternalChordEngine(ChordEngine):

    def __init__(self):
        super().__init__(AppParameterType.EXTERNAL_CHORD_ENGINE)

        self.noteHistory = NoteHistory()

        self.chords = {
            ChordButton.SOUTH: Chord([0, 3, 7], [0], 0),
            ChordButton.WEST: Chord([0, 3, 7], [0], 0),
            ChordButton.NORTH: Chord([0, 3, 7], [0], 0),
            ChordButton.EAST: Chord([0, 3, 7], [0], 0)
        }

    def handleMidiMessage(self, message: MidiInputMessage):
        if message.type == MidiInputMessageType.NOTE_ON:
            self.handleNoteOn(message.note)
        elif message.type == MidiInputMessageType.NOTE_OFF:
            self.handleNoteOff(message.note)

    def handleNoteOn(self, note: int):
        updates = self.noteHistory.noteOn(note)
        if (state.chordMode == ExternalChordMode.MOST_RECENT_NOTE_SET and updates.lastContiguousClassesChanged):
            self.determineChordAndScale()
        
    def handleNoteOff(self, note: int):
        self.noteHistory.noteOff(note)

    def getChordNoteClasses(self):
        chord = self.chords[state.chord.activeButton]
        rootType = chord.getRoot()
        chordTypes = chord.getNoteTypes()
        return chordTypes, rootType

    def getChordNotes(self, button: ChordButton):
        chord = self.chords[button]
        chordNotes = chord.getChord()
        chordAdjustedOctaves = self.chordOctave.apply(chordNotes)
        return chordAdjustedOctaves

    def getBassNote(self):
        chord = self.chords[state.chord.activeButton]
        return chord.getBass()
        
    def determineChordAndScale(self):
        if state.chordMode == ExternalChordMode.MOST_RECENT_NOTE_SET:
            noteClasses = state.noteInHistory.lastContiguousClasses
            key, scale = self.getScaleAndKey(noteClasses)
            print(f"key: {key}, scale: {scale}")

            self.scale.update(scale)
            self.key.set(key)

            lowestClass = state.noteInHistory.lowestInContiguousClasses % 12
            rootClass = lowestClass
            print(f"rootClass: {rootClass}")

            keyAgnosticRoot = self.rotateBack(key, [rootClass])[0]
            print(f"keyAgnosticRoot: {keyAgnosticRoot}")

            keyAgnosticChord = self.rotateBack(key, noteClasses)
            print(f"keyAgnosticChord: {keyAgnosticChord}")

            rootIndex = scale.index(keyAgnosticRoot)
            print(f"rootIndex: {rootIndex}")

            chordIndecies = [scale.index(noteClass) for noteClass in keyAgnosticChord]
            print(f"chordIndecies: {chordIndecies}")

            chordIndeciesFromRoot = [(chordIndex + (len(scale) - rootIndex)) % len(scale) for chordIndex in chordIndecies]
            chordIndeciesFromRoot.sort()
            print(f"chordIndeciesFromRoot: {chordIndeciesFromRoot}")

            self.chords[ChordButton.SOUTH] = Chord(chordIndeciesFromRoot, chordIndeciesFromRoot, rootIndex, scale)
            self.chords[ChordButton.WEST] = Chord(chordIndeciesFromRoot, chordIndeciesFromRoot, rootIndex, scale)
            self.chords[ChordButton.NORTH] = Chord(chordIndeciesFromRoot, chordIndeciesFromRoot, rootIndex, scale)
            self.chords[ChordButton.EAST] = Chord(chordIndeciesFromRoot, chordIndeciesFromRoot, rootIndex, scale)

    def getScaleAndKey(self, noteClasses: List[int]) -> Tuple[int, List[int]]:
        for scale in state.preferredScaleClasses:
            possibleRotations: List[int] = []
            for r in range(12):
                rotatedScale = self.rotateForward(r, scale)
                if self.notesFitInScale(noteClasses, rotatedScale):
                    possibleRotations.append(r)
            if len(possibleRotations) == 0:
                continue
            elif len(possibleRotations) == 1:
                return possibleRotations[0], scale
            elif len(possibleRotations) > 1:
                if state.scaleMode == ExternalChordScaleMode.LAST_SEVEN:
                    lastSeven = state.noteInHistory.classRecencyRanking[:7]
                    if not self.notesFitInScale(noteClasses, lastSeven):
                        return self.useNotesAsScale(noteClasses)
                    for r in possibleRotations:
                        rotatedScale = self.rotateForward(r, scale)
                        if self.notesFitInScale(lastSeven, rotatedScale):
                            return r, rotatedScale
        if not self.notesFitInScale(noteClasses, lastSeven):
            return self.useNotesAsScale(noteClasses)
        else:
            return self.useNotesAsScale(lastSeven)
                    
    def useNotesAsScale(self, noteClasses: List[int]) -> Tuple[int, List[int]]:
        if len(noteClasses) == 0:
            return 0, []
        return noteClasses[0], self.rotateBack(noteClasses[0], noteClasses)
        
    def notesFitInScale(self, noteClasses: List[int], scale: List[int]) -> bool:
        for chordClass in noteClasses:
            if chordClass not in scale:
                return False
        return True

    def getPrimeForm(self, noteClasses: List[int]):
        classes = [n for n in noteClasses]
        classes.sort()
        lowestSum = 66
        primeForm = []

        for note in classes:
            roatatedClasses = self.rotateBack(note, classes)
            roatatedClasses.sort()
            roatationSum = sum(roatatedClasses)
            if roatationSum < lowestSum:
                lowestSum = roatationSum
                primeForm = roatatedClasses

        return primeForm

    def rotateBack(self, r: int, noteClasses: List[int]) -> List[int]:
        newClasses = [(noteClass + (12 - r)) % 12 for noteClass in noteClasses]
        newClasses.sort()
        return newClasses

    def rotateForward(self, r: int, noteClasses: List[int]) -> List[int]:
        newClasses = [(noteClass + r) % 12 for noteClass in noteClasses]
        newClasses.sort()
        return newClasses
    