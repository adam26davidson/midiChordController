from typing import Callable

from pyrsistent import thaw

from constants import MAX_VOICE_COUNT
from models.appParameter import AppParameter, AppParameterType
from models.command import Command
from models.commandType import CommandType
from redux import store
from redux import utils as redux_utils
from redux.actions import musicEngine as actions
from redux.settingsStorage import settings_storage_utility

from ..chordEngineState import state


class VoiceCount:

    update_chord_engine: Callable
    type: AppParameterType

    def __init__(self, type: AppParameterType, update_chord_engine: Callable):
        self.update_chord_engine = update_chord_engine
        self.type = type

        store.subscribe(self.__handle_store_update)
        store.dispatch(actions.change_voice_count(state.voice_count))

        redux_utils.add_app_parameters(self.__get_parameters())

    def set(self, count):
        count = max(min(count, MAX_VOICE_COUNT), 1)
        state.voice_count = count
        store.dispatch(actions.change_voice_count(state.voice_count))
        settings_storage_utility.save_settings()
        self.update_chord_engine()

    def increment(self):
        self.set(state.voice_count + 1)

    def decrement(self):
        self.set(state.voice_count - 1)

    def __handle_store_update(self):
        me_state = thaw(store.get_state()['musicEngine'])
        if (me_state['voiceCount'] != state.voice_count):
            self.set(me_state['voiceCount'])

    def __get_parameters(self):
        key_prefix = "EXTERNAL_" if self.type == AppParameterType.EXTERNAL_CHORD_ENGINE else "INTERNAL_"
        return [
            AppParameter(
                valid_command_types = [CommandType.INCREMENTAL],
                command_mappings = {
                    Command.INCREMENT: self.increment,
                    Command.DECREMENT: self.decrement
                },
                key = f"{key_prefix}VOICE_COUNT",
                label = "Voice Count",
                label_abreviation="V",
                type = self.type
            )
        ]
