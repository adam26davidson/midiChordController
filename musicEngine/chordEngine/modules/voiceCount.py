from typing import Callable
from constants import MAX_SPREAD_OCTAVES, MAX_VOICE_COUNT, SPREAD_STEPS_PER_OCTAVE
from models.appParameter import AppParameter, AppParameterType
from models.command import Command
from models.commandType import CommandType
from redux import store
from redux.actions import musicEngine as actions
from redux.settingsStorage import SettingsStorageUtility
from ..chordEngineState import state
from pyrsistent import thaw
from redux import utils as reduxUtils


class VoiceCount():

    updateChordEngine: Callable
    type: AppParameterType
    
    def __init__(self, type: AppParameterType, updateChordEngine: Callable):
        self.updateChordEngine = updateChordEngine
        self.type = type

        store.subscribe(self.__handleStoreUpdate)
        store.dispatch(actions.changeVoiceCount(state.voiceCount))

        reduxUtils.addAppParameters(self.__getParameters())

    def set(self, count):
        count = max(min(count, MAX_VOICE_COUNT), 1)
        state.voiceCount = count
        store.dispatch(actions.changeVoiceCount(state.voiceCount))
        SettingsStorageUtility.saveSettings()
        self.updateChordEngine()

    def increment(self):
        self.set(state.voiceCount + 1)

    def decrement(self):
        self.set(state.voiceCount - 1)

    def __handleStoreUpdate(self):
        meState = thaw(store.get_state()['musicEngine'])
        if (meState['voiceCount'] != state.voiceCount):
            self.set(meState['voiceCount'])

    def __getParameters(self):
        keyPrefix = str(self.type.value).upper() + "_"
        return [
            AppParameter(
                validCommandTypes = [CommandType.INCREMENTAL],
                commandMappings = {
                    Command.INCREMENT: self.increment, 
                    Command.DECREMENT: self.decrement
                },
                key = f"{keyPrefix}VOICE_COUNT",
                label = "Voice Count",
                labelAbreviation="V",
                type = self.type
            )
        ]

