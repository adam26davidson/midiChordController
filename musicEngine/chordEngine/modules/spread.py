from typing import Callable
from constants import MAX_SPREAD_OCTAVES, SPREAD_STEPS_PER_OCTAVE
from models.appParameter import AppParameter, AppParameterType
from models.command import Command
from models.commandType import CommandType
from redux import store
from redux.actions import musicEngine as actions
from redux.settingsStorage import SettingsStorageUtility
from ..chordEngineState import state
from pyrsistent import thaw
from redux import utils as reduxUtils


class Spread():

    updateChordEngine: Callable
    type: AppParameterType
    
    def __init__(self, type: AppParameterType, updateChordEngine: Callable):
        self.updateChordEngine = updateChordEngine
        self.type = type
        store.subscribe(self.__handleStoreUpdate)
        store.dispatch(actions.changeSpread(state.spread))

        reduxUtils.addAppParameters(self.__getParameters())

    def set(self, spread):
        maxSpread = SPREAD_STEPS_PER_OCTAVE * MAX_SPREAD_OCTAVES - 1
        spread = max(min(spread, maxSpread), 0)
        state.spread = spread
        store.dispatch(actions.changeSpread(state.spread))
        SettingsStorageUtility.saveSettings()
        self.updateChordEngine()
        
    def increment(self):
        self.set(state.spread + 1)

    def decrement(self):
        self.set(state.spread - 1)

    def __handleStoreUpdate(self):
        meState = thaw(store.get_state()['musicEngine'])
        if (meState['spread'] != state.spread):
            self.set(meState['spread'])

    def __getParameters(self):
        return [
            AppParameter(
                validCommandTypes = [CommandType.INCREMENTAL],
                commandMappings = {
                    Command.INCREMENT: self.increment, 
                    Command.DECREMENT: self.decrement
                },
                key = "SPREAD",
                label = "Spread",
                labelAbreviation="S",
                type = self.type
            )
        ]
