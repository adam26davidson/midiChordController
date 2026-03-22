from __future__ import annotations

import math
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from constants import INVERSION_SNAP, MAX_INVERSION_RANGE

if TYPE_CHECKING:
    from collections.abc import Callable
from models.app_parameter import AppParameter, AppParameterType
from models.command import Command  # noqa: F401
from models.command_type import CommandType  # noqa: F401
from music_engine.chord_engine.state.inversion_state import InversionState
from redux import store
from redux import utils as redux_utils
from redux.actions import music_engine as actions  # noqa: F401

from ...chord_engine_state import state  # noqa: F401


class Inversion(ABC):

    update_chord_engine: Callable[[], None]
    type: AppParameterType

    def __init__(self, type: AppParameterType, update_chord_engine: Callable[[], None]) -> None:
        self.update_chord_engine = update_chord_engine
        self.type = type

        store.subscribe(self.handle_store_update)

        self.update_redux_range()
        self.update_redux_value()

        redux_utils.add_app_parameters(self.get_parameters())

    @abstractmethod
    def get_state(self) -> InversionState:
        pass

    @abstractmethod
    def update_redux_value(self) -> None:
        pass

    @abstractmethod
    def update_redux_range(self) -> None:
        pass

    @abstractmethod
    def update_redux_locked(self) -> None:
        pass

    @abstractmethod
    def handle_store_update(self) -> None:
        pass

    @abstractmethod
    def get_parameters(self) -> list[AppParameter]:
        pass

    def increment_range(self) -> None:
        self.set_range(self.get_state().range + 1)

    def decrement_range(self) -> None:
        self.set_range(self.get_state().range - 1)

    def set_range(self, range: int) -> None:
        range = max(min(range, MAX_INVERSION_RANGE), 0)
        self.get_state().range = range
        old_inversion = self.get_state().value
        self.get_state().value = max(min(old_inversion, range), -1*range)

        self.update_chord_engine()
        self.update_redux_range()
        self.update_redux_value()

    def increment(self) -> None:
        new_inversion = self.get_state().value + 1
        if abs(new_inversion) <= self.get_state().range:
            self.set_value(new_inversion)

    def decrement(self) -> None:
        new_inversion = self.get_state().value - 1
        if abs(new_inversion) <= self.get_state().range:
            self.set_value(new_inversion)

    def set_value(self, inversion: int) -> None:
        if (not self.get_state().locked) and inversion != self.get_state().value:
                range = self.get_state().range
                self.get_state().value = max(min(inversion, range), -1*range)
                self.update_chord_engine()
                self.update_redux_value()

    def set_analog_value(self, value: float) -> None:
        inversion = self.process_value(value)
        self.set_value(inversion)

    def toggle_lock(self) -> None:
        self.get_state().locked = not self.get_state().locked
        self.update_redux_locked()

    def process_value(self, raw_value: float) -> int:
        max_steps = self.get_state().range
        last_value = self.get_state().value

        # converts to an integer in the correct inversion range
        def get_value(x: float) -> int:
            return math.floor(((x+1)/2)*((2*max_steps)+1)) - max_steps

        # snap processed value back into current window if within snap region
        value = get_value(raw_value)
        snap = (1.0 / (max_steps + 1)) * INVERSION_SNAP
        if value == last_value + 1:
            raw_value -= snap
            value = get_value(raw_value)
        if value == last_value - 1:
            raw_value += snap
            value = get_value(raw_value)

        return value


