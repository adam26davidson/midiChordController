from abc import ABC, abstractmethod
from typing import Callable, List
from models.appParameter import AppParameter, AppParameterType
from models.command import Command
from models.commandType import CommandType
from musicEngine.chordEngine.chordEngineMessage import ChordEngineMessage, ChordPlayer, ChordEngineMessageType
from musicEngine.chordEngine.modules.spread import Spread
from musicEngine.chordEngine.modules.chordOctave import ChordOctave
from musicEngine.chordEngine.state.chordsState import ChordButton
from musicEngine.chordEngine.modules.hold import Hold
from musicEngine.chordEngine.modules.inversion.bassPosition import BassPosition
from musicEngine.chordEngine.modules.inversion.chordInversion import ChordInversion
from musicEngine.chordEngine.modules.key import Key
from musicEngine.chordEngine.modules.scale import Scale
from musicEngine.chordEngine.modules.voiceCount import VoiceCount
from .chordEngineState import state
from redux import store
from redux.actions import musicEngine as actions
from redux import utils as reduxUtils


class ChordEngine(ABC):

    type: AppParameterType

    scale: Scale
    inversion: ChordInversion
    bassPosition: BassPosition
    key: Key
    spread: Spread
    chordOctave: ChordOctave
    voiceCount: VoiceCount
    hold: Hold

    callbacks: List[Callable]

    def __init__(self, type: AppParameterType):

        self.type = type

        self.scale = Scale()
        self.inversion = ChordInversion(type, self.updateChord)
        self.bassPosition = BassPosition(type, self.updateBass)
        self.key = Key(type, self.updateChordType)
        self.spread = Spread(type, self.updateChord)
        self.chordOctave = ChordOctave(type, self.updateChord)
        self.voiceCount = VoiceCount(type, self.updateChord)
        self.hold = Hold(type, self.stopChordAndBass)

        self.callbacks = []

        reduxUtils.addAppParameters(self.getParameters())

    @abstractmethod
    def getChordNoteClasses(self):
        pass

    @abstractmethod
    def getChordNotes(self, button):
        pass

    @abstractmethod
    def getBassNote(self):
        pass    

    def subscribe(self, callback):
        self.callbacks.append(callback)

    def sendMessage(self, message):
        for callback in self.callbacks:
            callback(message)

    def sendNotesOn(self, notes: List[int], player: ChordPlayer):
        message = ChordEngineMessage(
            type=ChordEngineMessageType.ON,
            notes=notes,
            player=player
        )
        self.sendMessage(message)

    def sendNotesOff(self, notes: List[int], player: ChordPlayer):
        message = ChordEngineMessage(
            type=ChordEngineMessageType.OFF,
            notes=notes,
            player=player
        )
        self.sendMessage(message)

    def chordButtonOn(self, button):
        if state.chord.buttonQueue.count(button) > 0:
            state.chord.buttonQueue.remove(button)
        state.chord.buttonQueue.append(button)
        self.updateChordFromControlState()

    def chordButtonOff(self, button):
        lastButton = state.chord.buttonQueue[-1]
        if state.chord.buttonQueue.count(button) > 0:
            state.chord.buttonQueue.remove(button)
        if button == lastButton:
            self.updateChordFromControlState()
    
    def updateChordFromControlState(self):
        if len(state.chord.buttonQueue) == 0:
            self.stopChord()
        else:
            button = state.chord.buttonQueue[-1]
            self.playChord(button)

    def playChord(self, button=None):
        if button is not None:
            state.chord.activeButton = button
        self.setChordType()
        self.stopChord(force=True)
        notes = self.getChordNotes(button)
        self.sendNotesOn(notes, player=ChordPlayer.CHORD)
        self.updateBass(fromChord=True)
        state.chord.playingNotes = notes
        state.chord.isPlaying = True

    def playBass(self):
        self.stopBass(buttonUp=False)
        bassNote = self.getBassNote()
        self.sendNotesOn([bassNote], player=ChordPlayer.BASS)
        store.dispatch(actions.playBass(bassNote))
        state.bass.playingNote = bassNote
        state.bass.isPlaying = True

    def stopChordAndBass(self):
        self.stopChord()
        self.stopBass(buttonUp=False)

    def stopChord(self, force=False):
        if ((not state.hold and state.chord.isPlaying) or force):
            playingNotes = state.chord.playingNotes
            self.sendNotesOff(playingNotes, player=ChordPlayer.CHORD)
            store.dispatch(actions.stopChord())
            state.chord.playingNotes = []
            state.chord.isPlaying = False

    def stopBass(self, buttonUp=True):
        if not (buttonUp and state.hold) and state.bass.isPlaying:
            playingBass = state.bass.playingNote
            self.sendNotesOff([playingBass], player=ChordPlayer.BASS)
            store.dispatch(actions.stopBass())
            state.bass.playingNote = None
            state.bass.isPlaying = False

    def updateChordType(self):
        self.setChordType()
        self.updateChord()
        self.updateBass()

    def setChordType(self):
        chordNoteClasses, rootClass = self.getChordNoteClasses()
        if chordNoteClasses != state.chord.NoteClasses or rootClass != state.chord.rootClass:
            state.chord.NoteClasses, state.chord.rootClass = chordNoteClasses, rootClass
            store.dispatch(actions.changeChordType({'chord': chordNoteClasses, 'root': rootClass}))

    def updateChord(self):
        if (state.chord.isPlaying):
            self.playChord(state.chord.activeButton)
        else:
            notes = self.getChordNotes(state.chord.activeButton)
            store.dispatch(actions.changeChordShadow(notes))

    def updateBass(self, fromChord=False):
        if (state.bass.isPlaying):
            if fromChord:
                bassNote = self.getBassNote()
                if state.bass.playingNote != bassNote:
                    self.playBass()
            else:
                self.playBass()
        else:
            note = self.getBassNote()
            store.dispatch(actions.changeBassShadow(note))

    def getParameters(self):
        keyPrefix = str(self.type.value).upper() + "_"
        return[
            AppParameter(
                validCommandTypes = [CommandType.ON_OFF],
                commandMappings = {
                    Command.ON: lambda: self.chordButtonOn(ChordButton.SOUTH), 
                    Command.OFF: lambda: self.chordButtonOff(ChordButton.SOUTH)
                },
                key = f"{keyPrefix}SOUTH_CHORD",
                label = "South Chord",
                labelAbreviation="S",
                type = self.type
            ),
            AppParameter(
                validCommandTypes = [CommandType.ON_OFF],
                commandMappings = {
                    Command.ON: lambda: self.chordButtonOn(ChordButton.WEST), 
                    Command.OFF: lambda: self.chordButtonOff(ChordButton.WEST)
                },
                key = f"{keyPrefix}WEST_CHORD",
                label = "West Chord",
                labelAbreviation="W",
                type = self.type
            ),
            AppParameter(
                validCommandTypes = [CommandType.ON_OFF],
                commandMappings = {
                    Command.ON: lambda: self.chordButtonOn(ChordButton.NORTH), 
                    Command.OFF: lambda: self.chordButtonOff(ChordButton.NORTH)
                },
                key = f"{keyPrefix}NORTH_CHORD",
                label = "North Chord",
                labelAbreviation="N",
                type = self.type
            ),
            AppParameter(
                validCommandTypes = [CommandType.ON_OFF],
                commandMappings = {
                    Command.ON: lambda: self.chordButtonOn(ChordButton.EAST), 
                    Command.OFF: lambda: self.chordButtonOff(ChordButton.EAST)
                },
                key = f"{keyPrefix}EAST_CHORD",
                label = "East Chord",
                labelAbreviation="E",
                type = self.type
            ),
            AppParameter(
                validCommandTypes = [CommandType.ON_OFF],
                commandMappings = {
                    Command.ON: self.playBass, 
                    Command.OFF: self.stopBass
                },
                key = f"{keyPrefix}BASS",
                label = "Bass",
                labelAbreviation="B",
                type = self.type
            )
        ]
