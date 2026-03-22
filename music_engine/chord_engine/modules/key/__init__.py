from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

from models.app_parameter import AppParameter, AppParameterType
from models.command import Command
from models.command_type import CommandType
from redux import get_music_engine_state, store
from redux import utils as redux_utils
from redux.actions import music_engine as actions
from redux.settings_storage import settings_storage_utility

from ...chord_engine_state import state


class Key:

    update_chord_engine: Callable[[], None]
    type: AppParameterType

    def __init__(self, type: AppParameterType, update_chord_engine: Callable[[], None]) -> None:
        self.update_chord_engine = update_chord_engine
        self.type = type
        store.subscribe(self.__handle_store_update)
        store.dispatch(actions.change_key(state.key.value))

        redux_utils.add_app_parameters(self.get_parameters())

    def __handle_store_update(self) -> None:
        me_state = get_music_engine_state()
        if (me_state['transposeIncrement'] != state.key.increment_by):
            self.set_increment_by(me_state['transposeIncrement'])
        if (me_state['key'] != state.key.value):
            self.set(me_state['key'])

    def set_increment_by(self, increment: int) -> None:
        state.key.increment_by = increment

    def increment(self) -> None:
        self.set(state.key.value + state.key.increment_by)

    def decrement(self) -> None:
        self.set(state.key.value + 12 - state.key.increment_by)

    def set(self, key: int) -> None:
        key = key % 12
        if state.key.value != key:
            state.key.value = key
            store.dispatch(actions.change_key(key))
            settings_storage_utility.save_settings()
            self.update_chord_engine()

    def get_parameters(self) -> list[AppParameter]:
        key_prefix = "EXTERNAL_" if self.type == AppParameterType.EXTERNAL_CHORD_ENGINE else "INTERNAL_"
        return [
            AppParameter(
                valid_command_types = [CommandType.INCREMENTAL],
                command_mappings = {
                    Command.INCREMENT: self.increment,
                    Command.DECREMENT: self.decrement
                },
                key = f"{key_prefix}KEY",
                label = "Transpose",
                label_abreviation="T",
                type = self.type
            )
        ]
