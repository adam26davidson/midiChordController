from typing import Callable

from models.app_parameter import AppParameter, AppParameterType
from models.command import Command
from models.command_type import CommandType
from redux import store
from redux import utils as redux_utils
from redux.actions import music_engine as actions

from ..chord_engine_state import state


class Hold:

    stop_chord_and_bass: Callable
    type: AppParameterType

    def __init__(self, type: AppParameterType, stop_chord_and_bass: Callable):
        self.stop_chord_and_bass = stop_chord_and_bass
        self.type = type

        store.dispatch(actions.change_hold(state.hold))
        redux_utils.add_app_parameters(self.__get_parameters())


    def toggle(self):
        if state.hold:
            state.hold = False
            self.stop_chord_and_bass()
        else:
            state.hold = True
        store.dispatch(actions.change_hold(state.hold))

    def __get_parameters(self):
        key_prefix = "EXTERNAL_" if self.type == AppParameterType.EXTERNAL_CHORD_ENGINE else "INTERNAL_"
        return [
            AppParameter(
                valid_command_types = [CommandType.TOGGLE],
                command_mappings = {
                    Command.TOGGLE: self.toggle
                },
                key = f"{key_prefix}HOLD",
                label = "Hold",
                label_abreviation="H",
                type = self.type
            )
        ]
