from pyrsistent import thaw

from models.app_parameter import AppParameter, AppParameterType
from models.command import Command
from models.command_type import CommandType
from music_engine.chord_engine.modules.inversion import Inversion
from music_engine.chord_engine.state.inversion_state import InversionState
from redux import store
from redux.actions import music_engine as actions

from ...chord_engine_state import state


class ChordInversion(Inversion):

    def __init__(self, type: AppParameterType, update_chord_engine: callable):
        super().__init__(type, update_chord_engine)

    def get_state(self) -> InversionState:
        return state.inversion

    def update_redux_value(self):
        store.dispatch(actions.change_inversion(state.inversion.value))

    def update_redux_range(self):
        store.dispatch(actions.change_inversion_range(state.inversion.range))

    def update_redux_locked(self):
        store.dispatch(actions.change_inversion_lock(state.inversion.locked))

    def handle_store_update(self):
        me_state = thaw(store.get_state()['musicEngine'])
        if (me_state['inversionRange'] != state.inversion.range):
            self.set_range(me_state['inversionRange'])

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
                key = f"{key_prefix}INVERSION",
                label = "Inversion",
                label_abreviation="I",
                type = self.type
            ),
            AppParameter(
                valid_command_types = [CommandType.TOGGLE],
                command_mappings = {
                    Command.TOGGLE: self.toggle_lock
                },
                key = f"{key_prefix}INVERSION_LOCK",
                label = "Inversion Lock",
                label_abreviation="IL",
                type = self.type
            ),
            AppParameter(
                valid_command_types = [CommandType.INCREMENTAL],
                command_mappings = {
                    Command.INCREMENT: self.increment_range,
                    Command.DECREMENT: self.decrement_range
                },
                key = f"{key_prefix}INVERSION_RANGE",
                label = "Inversion Range",
                label_abreviation="IR",
            )
        ]
