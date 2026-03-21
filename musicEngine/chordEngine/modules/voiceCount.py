from typing import Callable

from pyrsistent import thaw

from constants import MAX_VOICE_COUNT
from models.appParameter import AppParameter, AppParameterType
from models.command import Command
from models.commandType import CommandType
from redux import store
from redux import utils as reduxUtils
from redux.actions import musicEngine as actions
from redux.settingsStorage import settingsStorageUtility

from ..chordEngineState import state


class VoiceCount:

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
        settingsStorageUtility.saveSettings()
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
        keyPrefix = "EXTERNAL_" if self.type == AppParameterType.EXTERNAL_CHORD_ENGINE else "INTERNAL_"
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

