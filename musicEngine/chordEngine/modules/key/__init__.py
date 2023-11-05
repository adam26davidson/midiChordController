from typing import Callable
from models.appParameter import AppParameter, AppParameterType
from models.command import Command
from models.commandType import CommandType
from redux import store
from redux.actions import musicEngine as actions
from redux.settingsStorage import SettingsStorageUtility
from redux import utils as reduxUtils
from ...chordEngineState import state
from pyrsistent import thaw


class Key():

    updateChordEngine: Callable
    type: AppParameterType

    def __init__(self, type: AppParameterType, updateChordEngine: Callable):
        self.updateChordEngine = updateChordEngine
        self.type = type
        store.subscribe(self.__handleStoreUpdate)
        store.dispatch(actions.changeKey(state.key.value))

        reduxUtils.addAppParameters(self.getParameters())

    def __handleStoreUpdate(self):
        meState = thaw(store.get_state()['musicEngine'])
        if (meState['transposeIncrement'] != state.key.incrementBy):
            self.setIncrementBy(meState['transposeIncrement'])
        if (meState['key'] != state.key.value):
            self.set(meState['key'])

    def setIncrementBy(self, increment):
        state.key.incrementBy = increment

    def increment(self):
        self.set(state.key.value + state.key.incrementBy)

    def decrement(self):
        self.set(state.key.value + 12 - state.key.incrementBy)

    def set(self, key):
        key = key % 12
        if state.key.value != key:
            state.key.value = key
            store.dispatch(actions.changeKey(key))
            SettingsStorageUtility.saveSettings()
            self.updateChordEngine()

    def getParameters(self):
        return [
            AppParameter(
                validCommandTypes = [CommandType.INCREMENTAL],
                commandMappings = {
                    Command.INCREMENT: self.chordEngine.incrementKey, 
                    Command.DECREMENT: self.chordEngine.decrementKey
                },
                key = "KEY",
                label = "Transpose",
                labelAbreviation="T",
                type = self.type
            )      
        ]