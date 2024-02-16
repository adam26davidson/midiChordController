import asyncio
import time
from typing import List, Tuple
from constants import MIDI_INPUT_STEP
from models.appParameter import AppParameterType
from musicEngine.chordEngine.chordEngine import ChordEngine
from musicEngine.chordEngine.externalChordEngine.modules.noteHistory import NoteHistory
from musicEngine.chordEngine.modules.chords import Chord
from musicEngine.chordEngine.state.chordsState import ChordButton
from musicEngine.midi.midiInputMessage import MidiInputMessage, MidiInputMessageType
from ..chordEngineState import ExternalChordMode, ExternalChordScaleMode, state


class ExternalChordEngine(ChordEngine):

    inputQueue: List[MidiInputMessage]
    noteHistory: NoteHistory

    def __init__(self):
        super().__init__(AppParameterType.EXTERNAL_CHORD_ENGINE)

        self.noteHistory = NoteHistory()
        self.inputQueue = []

        self.chords = {
            ChordButton.SOUTH: Chord([0, 3, 7], [0], 0),
            ChordButton.WEST: Chord([0, 3, 7], [0], 0),
            ChordButton.NORTH: Chord([0, 3, 7], [0], 0),
            ChordButton.EAST: Chord([0, 3, 7], [0], 0)
        }

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

    def start(self):
        asyncio.ensure_future(self.__inputLoop())

    def handleMidiMessage(self, message: MidiInputMessage):
        self.inputQueue.append(message)

    async def __inputLoop(self):
        while True:
            if len(self.inputQueue) > 0:
                self.processQueue(self.inputQueue)
            await asyncio.sleep(MIDI_INPUT_STEP)

    def processQueue(self, queue: List[MidiInputMessage]):
        lastContiguousClasses = [c for c in state.noteInHistory.lastContiguousClasses]
        lastContiguousClasses.sort()
        for message in queue:
            if message.type == MidiInputMessageType.NOTE_ON:
                self.noteHistory.noteOn(message.note)
            elif message.type == MidiInputMessageType.NOTE_OFF:
                self.noteHistory.noteOff(message.note)
        newContiguousClasses = [c for c in state.noteInHistory.lastContiguousClasses]
        newContiguousClasses.sort()
        self.inputQueue = []
        if lastContiguousClasses != newContiguousClasses:
            print("new chord")
            self.determineChordAndScale()
        
    def determineChordAndScale(self):
        if state.chordMode == ExternalChordMode.MOST_RECENT_NOTE_SET:
            noteClasses = state.noteInHistory.lastContiguousClasses
            key, scale = self.getScaleAndKey(noteClasses)

            self.scale.update(scale)
            self.key.set(key)

            lowestClass = state.noteInHistory.lowestInContiguousClasses % 12
            rootClass = lowestClass
            keyAgnosticRoot = self.rotateBack(key, [rootClass])[0]
            keyAgnosticChord = self.rotateBack(key, noteClasses)
            rootIndex = scale.index(keyAgnosticRoot)

            chordIndecies = [scale.index(noteClass) for noteClass in keyAgnosticChord]
            chordIndeciesFromRoot = [(chordIndex + (len(scale) - rootIndex)) % len(scale) for chordIndex in chordIndecies]
            chordIndeciesFromRoot.sort()
            
            if len(chordIndeciesFromRoot) > 1:
                NoRootchordIndeciesFromRoot = chordIndeciesFromRoot[1:]
            else:
                NoRootchordIndeciesFromRoot = chordIndeciesFromRoot

            scaleChordIndecies = range(1, len(scale) + 1)
            print("key agnostic scale: ", scale)
            print("key: ", key)

            print("chordIndeciesFromRoot: ", chordIndeciesFromRoot)
            print("rootIndex: ", rootIndex)

            if len(self.inputQueue) > 0:
                print("aborting chord update")
                return
            southChord = Chord(chordIndeciesFromRoot, chordIndeciesFromRoot, rootIndex, scale)
            if len(self.inputQueue) > 0:
                print("aborting chord update")
                return
            westChord = Chord(NoRootchordIndeciesFromRoot, chordIndeciesFromRoot, rootIndex, scale)
            if len(self.inputQueue) > 0:
                print("aborting chord update")
                return
            northChord = Chord(scaleChordIndecies, scaleChordIndecies, 0, scale)
            if len(self.inputQueue) > 0:
                print("aborting chord update")
                return
            eastChord = Chord(scaleChordIndecies, scaleChordIndecies, 0, scale)
            if len(self.inputQueue) > 0:
                print("aborting chord update")
                return

            self.chords[ChordButton.SOUTH] = southChord
            self.chords[ChordButton.WEST] = westChord
            self.chords[ChordButton.NORTH] = northChord
            self.chords[ChordButton.EAST] = eastChord

            self.updateChordType()

    def getScaleAndKey(self, noteClasses: List[int]) -> Tuple[int, List[int]]:
        lastSeven = state.noteInHistory.classRecencyRanking[:7]
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
                    if not self.notesFitInScale(noteClasses, lastSeven):
                        return self.useNotesAsScale(noteClasses)
                    for r in possibleRotations:
                        rotatedScale = self.rotateForward(r, scale)
                        if self.notesFitInScale(lastSeven, rotatedScale):
                            return r, scale
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
    