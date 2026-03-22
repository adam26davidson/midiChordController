from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

from models.app_parameter import AppParameter, AppParameterType
from models.command import Command
from models.command_type import CommandType
from music_engine.chord_engine.modules.inversion import Inversion
from music_engine.chord_engine.state.inversion_state import InversionState
from redux import get_music_engine_state, store
from redux.actions import music_engine as actions

from ...chord_engine_state import state


class BassPosition(Inversion):

    def __init__(self, type: AppParameterType, update_chord_engine: Callable[[], None]) -> None:
        super().__init__(type, update_chord_engine)

    def get_state(self) -> InversionState:
        return state.bass_position

    def update_redux_value(self) -> None:
        store.dispatch(actions.change_bass_position(state.bass_position.value))

    def update_redux_range(self) -> None:
        store.dispatch(actions.change_bass_range(state.bass_position.range))

    def update_redux_locked(self) -> None:
        # Intentional no-op: bass position lock is not displayed in the UI,
        # unlike chord inversion lock which dispatches to Redux for display.
        pass

    def handle_store_update(self) -> None:
        me_state = get_music_engine_state()
        if (me_state['bassRange'] != state.bass_position.range):
            self.set_range(me_state['bassRange'])

    def get_parameters(self) -> list[AppParameter]:
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
