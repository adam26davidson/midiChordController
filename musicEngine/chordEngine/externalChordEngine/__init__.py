import asyncio
import threading

from constants import MIDI_INPUT_STEP
from models.appParameter import AppParameterType
from musicEngine.chordEngine.chordEngine import ChordEngine
from musicEngine.chordEngine.externalChordEngine.modules.noteHistory import NoteHistory
from musicEngine.chordEngine.modules.chords import Chord
from musicEngine.chordEngine.state.chordsState import ChordButton
from musicEngine.midi.midiInputMessage import MidiInputMessage, MidiInputMessageType

from ..chordEngineState import ExternalChordMode, ExternalChordScaleMode, state


class ExternalChordEngine(ChordEngine):

    inputQueue: list[MidiInputMessage]
    noteHistory: NoteHistory

    def __init__(self):
        super().__init__(AppParameterType.EXTERNAL_CHORD_ENGINE)

        self.noteHistory = NoteHistory()
        self.inputQueue = []
        self.inputQueueLock = threading.Lock()

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
        _task = asyncio.ensure_future(self.__inputLoop())

    def handleMidiMessage(self, message: MidiInputMessage):
        with self.inputQueueLock:
            self.inputQueue.append(message)

    async def __inputLoop(self):
        while True:
            with self.inputQueueLock:
                queue = self.inputQueue
                self.inputQueue = []
            if len(queue) > 0:
                self.processQueue(queue)
            await asyncio.sleep(MIDI_INPUT_STEP)

    def processQueue(self, queue: list[MidiInputMessage]):
        lastContiguousClasses = list(state.noteInHistory.lastContiguousClasses)
        lastContiguousClasses.sort()
        for message in queue:
            if message.type == MidiInputMessageType.NOTE_ON:
                self.noteHistory.noteOn(message.note)
            elif message.type == MidiInputMessageType.NOTE_OFF:
                self.noteHistory.noteOff(message.note)
        newContiguousClasses = list(state.noteInHistory.lastContiguousClasses)
        newContiguousClasses.sort()
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

            southChord = Chord(chordIndeciesFromRoot, chordIndeciesFromRoot, rootIndex, scale)
            westChord = Chord(NoRootchordIndeciesFromRoot, chordIndeciesFromRoot, rootIndex, scale)
            northChord = Chord(scaleChordIndecies, scaleChordIndecies, 0, scale)
            eastChord = Chord(scaleChordIndecies, scaleChordIndecies, 0, scale)

            self.chords[ChordButton.SOUTH] = southChord
            self.chords[ChordButton.WEST] = westChord
            self.chords[ChordButton.NORTH] = northChord
            self.chords[ChordButton.EAST] = eastChord

            self.updateChordType()

    def getScaleAndKey(self, noteClasses: list[int]) -> tuple[int, list[int]]:
        lastSeven = state.noteInHistory.classRecencyRanking[:7]
        for scale in state.preferredScaleClasses:
            possibleRotations: list[int] = []
            for r in range(12):
                rotatedScale = self.rotateForward(r, scale)
                if self.notesFitInScale(noteClasses, rotatedScale):
                    possibleRotations.append(r)
            if len(possibleRotations) == 0:
                continue
            if len(possibleRotations) == 1:
                return possibleRotations[0], scale
            if (len(possibleRotations) > 1
                    and state.scaleMode == ExternalChordScaleMode.LAST_SEVEN):
                    if not self.notesFitInScale(noteClasses, lastSeven):
                        return self.useNotesAsScale(noteClasses)
                    for r in possibleRotations:
                        rotatedScale = self.rotateForward(r, scale)
                        if self.notesFitInScale(lastSeven, rotatedScale):
                            return r, scale
        if not self.notesFitInScale(noteClasses, lastSeven):
            return self.useNotesAsScale(noteClasses)
        return self.useNotesAsScale(lastSeven)

    def useNotesAsScale(self, noteClasses: list[int]) -> tuple[int, list[int]]:
        if len(noteClasses) == 0:
            return 0, []
        return noteClasses[0], self.rotateBack(noteClasses[0], noteClasses)

    def notesFitInScale(self, noteClasses: list[int], scale: list[int]) -> bool:
        return all(chordClass in scale for chordClass in noteClasses)

    def getPrimeForm(self, noteClasses: list[int]):
        classes = list(noteClasses)
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

    def rotateBack(self, r: int, noteClasses: list[int]) -> list[int]:
        newClasses = [(noteClass + (12 - r)) % 12 for noteClass in noteClasses]
        newClasses.sort()
        return newClasses

    def rotateForward(self, r: int, noteClasses: list[int]) -> list[int]:
        newClasses = [(noteClass + r) % 12 for noteClass in noteClasses]
        newClasses.sort()
        return newClasses
