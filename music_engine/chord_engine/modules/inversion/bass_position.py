from typing import Callable

from pyrsistent import thaw

from models.app_parameter import AppParameter, AppParameterType
from models.command import Command
from models.command_type import CommandType
from music_engine.chord_engine.modules.inversion import Inversion
from music_engine.chord_engine.state.inversion_state import InversionState
from redux import store
from redux.actions import music_engine as actions

from ...chord_engine_state import state


class BassPosition(Inversion):

    def __init__(self, type: AppParameterType, update_chord_engine: Callable):
        super().__init__(type, update_chord_engine)

    def get_state(self) -> InversionState:
        return state.bass_position

    def update_redux_value(self):
        store.dispatch(actions.change_bass_position(state.bass_position.value))

    def update_redux_range(self):
        store.dispatch(actions.change_bass_range(state.bass_position.range))

    def update_redux_locked(self):
        pass

    def handle_store_update(self):
        me_state = thaw(store.get_state()['musicEngine'])
        if (me_state['bassRange'] != state.bass_position.range):
            self.set_range(me_state['bassRange'])

    def get_parameters(self):
        key_prefix = "EXTERNAL_" if self.type == AppParameterType.EXTERNAL_CHORD_ENGINE else "INTERNAL_"
        return [
            AppParameter(
                valid_command_types = [CommandType.ANALOG, CommandType.INCREMENTAL],
                command_mappings = {
                    Command.UPDATE: self.set_analog_value,
                    Command.INCREMENT: self.increment,
                    Command.DECREMENT: self.decrement
                },
                key = f"{key_prefix}BASS_POSITION",
                label = "Bass Position",
                label_abreviation="BP",
                type = self.type
            ),
            AppParameter(
                valid_command_types = [CommandType.TOGGLE],
                command_mappings = {
                    Command.TOGGLE: self.toggle_lock
                },
                key = f"{key_prefix}BASS_POSITION_LOCK",
                label = "Bass Position Lock",
                label_abreviation="BL",
                type = self.type
            ),
            AppParameter(
                valid_command_types = [CommandType.INCREMENTAL],
                command_mappings = {
                    Command.INCREMENT: self.increment_range,
                    Command.DECREMENT: self.decrement_range
                },
                key = f"{key_prefix}BASS_POSITION_RANGE",
                label = "Bass Range",
                label_abreviation="BR",
                type = self.type
            )
        ]
