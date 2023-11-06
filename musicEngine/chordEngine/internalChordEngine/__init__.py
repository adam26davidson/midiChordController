from models.appParameter import AppParameter, AppParameterType
from models.command import Command
from models.commandType import CommandType
from musicEngine.chordEngine.chordEngine import ChordEngine
from musicEngine.chordEngine.internalChordEngine.modules.alternate import Alternate
from musicEngine.chordEngine.internalChordEngine.modules.modulations import Modulations
from musicEngine.chordEngine.internalChordEngine.modules.secondaries import Secondaries
from musicEngine.chordEngine.state.secondariesState import SecondarySide
from ..modules.chords.dualChord import DualChord
from ..state.chordsState import ChordButton

from ..chordEngineState import state
from constants import SETTINGS
from redux import store
from redux.actions import musicEngine as actions
from redux import utils as reduxUtils


class InternalChordEngine(ChordEngine):

    modulations: Modulations

    def __init__(self):
        super().__init__(AppParameterType.INTERNAL_CHORD_ENGINE)

        self.alternate = Alternate(self.updateChordType)
        store.dispatch(actions.changeSettingsList([s['name'] for s in SETTINGS]))
        self.loadSetting(state.internalSettings.index)

        reduxUtils.addAppParameters(self.getInternalParamters())

    def incrementSetting(self):
        self.loadSetting((state.internalSettings.index + 1) % len(SETTINGS))

    def decrementSetting(self):
        newIndex = state.internalSettings.index - 1
        if (newIndex < 0):
            newIndex = len(SETTINGS) - 1
        self.loadSetting(newIndex)

    def loadSetting(self, index):
        state.internalSettings.loading = True
        store.dispatch(actions.changeSettingLoading(True))

        self.stopChordAndBass()

        state.internalSettings.index = index
        setting = SETTINGS[index]

        self.scale.update(setting['scale'])

        self.chords = {
            ChordButton.SOUTH: DualChord(setting["chords"][ChordButton.SOUTH.value], state.scale.keyAgnostic),
            ChordButton.WEST: DualChord(setting["chords"][ChordButton.WEST.value], state.scale.keyAgnostic),
            ChordButton.NORTH: DualChord(setting["chords"][ChordButton.NORTH.value], state.scale.keyAgnostic),
            ChordButton.EAST: DualChord(setting["chords"][ChordButton.EAST.value], state.scale.keyAgnostic)
        }

        self.secondaries = Secondaries(setting["secondaries"], self.updateChordType)
        self.modulations = Modulations(setting["modulations"], self.updateChordType)

        state.chord.NoteClasses, state.chord.rootClass = self.getChordNoteClasses()

        store.dispatch(actions.changeSetting(index))
        store.dispatch(actions.changeChordType({
            'chord': state.chord.NoteClasses,
            'root': state.chord.rootClass
        }))
        shadowChord = self.getChordNotes(state.chord.activeButton)
        store.dispatch(actions.changeChordShadow(shadowChord))
        store.dispatch(actions.changeBassShadow(self.getBassNote()))

        store.dispatch(actions.changeSettingLoading(False))
        state.internalSettings.loading = False

    def getChordNoteClasses(self):
        chord = self.chords[state.chord.activeButton]
        scale = self.scale.get()
        if (state.secondary.side == SecondarySide.NONE):
            rootType = self.modulations.applyOne(chord.getRoot(), scale)
            modulatedTypes = self.modulations.apply(chord.getNoteTypes(), scale)
            return [note % 12 for note in modulatedTypes], rootType % 12
        else:
            chordRoot = self.modulations.apply(chord.getRoot(), scale)
            rootType = self.secondaries.getRoot(chordRoot)
            chordType = self.secondaries.getNoteTypes(chordRoot)
            chordType.sort()
            return chordType, rootType

    def getChordNotes(self, button: ChordButton):
        chord = self.chords[button]
        chordNotes = []

        if (state.secondary.side == SecondarySide.NONE):
            modlessChord = chord.getChord()
            chordNotes = self.modulations.apply(modlessChord, self.scale.get())
        else:
            modulatedRoot = self.modulations.applyOne(chord.getRoot(), self.scale.get())
            chordNotes = self.secondaries.getChord(modulatedRoot)

        chordAdjustedOctaves = self.chordOctave.apply(chordNotes)
        return chordAdjustedOctaves

    def getBassNote(self):
        chord = self.chords[state.chord.activeButton]

        if (state.secondary.side == SecondarySide.NONE):
            bass = chord.getBass()
            return self.modulations.applyOne(bass, self.scale.get())
        else:
            chordRoot = self.modulations.applyOne(chord.getRoot(), self.scale.get())
            return self.secondaries.getBass(chordRoot)
        
    def getInternalParamters(self):
        return [
            AppParameter(
                validCommandTypes = [CommandType.INCREMENTAL],
                commandMappings = {
                    Command.INCREMENT: self.incrementSetting, 
                    Command.DECREMENT: self.decrementSetting
                },
                key = "SETTING",
                label = "Patch",
                labelAbreviation="P",
                type = AppParameterType.INTERNAL_CHORD_ENGINE
            )
        ]
