from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

from constants import MAX_SPREAD_OCTAVES, SPREAD_STEPS_PER_OCTAVE
from models.app_parameter import AppParameter, AppParameterType
from models.command import Command
from models.command_type import CommandType
from redux import get_music_engine_state, store
from redux import utils as redux_utils
from redux.actions import music_engine as actions
from redux.settings_storage import settings_storage_utility

from ..chord_engine_state import state


class Spread:

    update_chord_engine: Callable[[], None]
    type: AppParameterType

    def __init__(self, type: AppParameterType, update_chord_engine: Callable[[], None]) -> None:
        self.update_chord_engine = update_chord_engine
        self.type = type
        store.subscribe(self.__handle_store_update)
        store.dispatch(actions.change_spread(state.spread))

        redux_utils.add_app_parameters(self.__get_parameters())

    def set(self, spread: int) -> None:
        max_spread = SPREAD_STEPS_PER_OCTAVE * MAX_SPREAD_OCTAVES - 1
        spread = max(min(spread, max_spread), 0)
        state.spread = spread
        store.dispatch(actions.change_spread(state.spread))
        settings_storage_utility.save_settings()
        self.update_chord_engine()

    def increment(self) -> None:
        self.set(state.spread + 1)

    def decrement(self) -> None:
        self.set(state.spread - 1)

    def __handle_store_update(self) -> None:
        me_state = get_music_engine_state()
        if (me_state['spread'] != state.spread):
            self.set(me_state['spread'])

    def __get_parameters(self) -> list[AppParameter]:
        key_prefix = "EXTERNAL_" if self.type == AppParameterType.EXTERNAL_CHORD_ENGINE else "INTERNAL_"
        return [
            AppParameter(
                valid_command_types = [CommandType.INCREMENTAL],
                command_mappings = {
                    Command.INCREMENT: self.increment,
                    Command.DECREMENT: self.decrement
                },
                key = f"{key_prefix}SPREAD",
                label = "Spread",
                label_abreviation="S",
                type = self.type
            )
        ]
