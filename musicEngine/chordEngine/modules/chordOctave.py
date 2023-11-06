from typing import Callable, List
from constants import MAX_OCTAVE_SHIFT, MAX_SPREAD_OCTAVES, SPREAD_STEPS_PER_OCTAVE
from models.appParameter import AppParameter, AppParameterType
from models.command import Command
from models.commandType import CommandType
from redux import store
from redux.actions import musicEngine as actions
from redux.settingsStorage import SettingsStorageUtility
from ..chordEngineState import state
from pyrsistent import thaw
from redux import utils as reduxUtils
from redux.settingsStorage import SettingsStorageUtility


class ChordOctave():

    updateChordEngine: Callable
    type: AppParameterType
    
    def __init__(self, type: AppParameterType, updateChordEngine: Callable):
        self.updateChordEngine = updateChordEngine
        self.type = type
        store.subscribe(self.__handleStoreUpdate)
        store.dispatch(actions.changeChordOctave(state.chordOctave))

        reduxUtils.addAppParameters(self.__getParameters())

    def __handleStoreUpdate(self):
        meState = thaw(store.get_state()['musicEngine'])
        if (meState['chordOctave'] != state.chordOctave):
            self.set(meState['chordOctave'])

    def apply(self, notes: List[int]) -> List[int]:
        return [note + (state.chordOctave * 12) for note in notes]

    def set(self, octave):
        clamped = max(min(octave, MAX_OCTAVE_SHIFT), -1*MAX_OCTAVE_SHIFT)
        state.chordOctave = clamped
        store.dispatch(actions.changeChordOctave(state.chordOctave))
        SettingsStorageUtility.saveSettings()
        self.updateChordEngine()

    def increment(self):
        self.set(state.chordOctave + 1)

    def decrement(self):
        self.set(state.chordOctave - 1)
        
    def __getParameters(self):
        keyPrefix = str(self.type.value).upper() + "_"
        return [
            AppParameter(
                validCommandTypes = [CommandType.INCREMENTAL],
                commandMappings = {
                    Command.INCREMENT: self.increment, 
                    Command.DECREMENT: self.decrement
                },
                key = f"{keyPrefix}OCTAVE",
                label = "Octave",
                labelAbreviation="O",
                type = self.type
            )
        ]
