import math
from abc import ABC, abstractmethod
from typing import Callable

from constants import INVERSION_SNAP, MAX_INVERSION_RANGE
from models.app_parameter import AppParameter, AppParameterType  # noqa: F401
from models.command import Command  # noqa: F401
from models.command_type import CommandType  # noqa: F401
from music_engine.chord_engine.state.inversion_state import InversionState
from redux import store
from redux import utils as redux_utils
from redux.actions import music_engine as actions  # noqa: F401

from ...chord_engine_state import state  # noqa: F401


class Inversion(ABC):

    update_chord_engine: Callable
    type: AppParameterType

    def __init__(self, type: AppParameterType, update_chord_engine: Callable):
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
    def update_redux_value(self):
        pass

    @abstractmethod
    def update_redux_range(self):
        pass

    @abstractmethod
    def update_redux_locked(self):
        pass

    @abstractmethod
    def handle_store_update(self):
        pass

    @abstractmethod
    def get_parameters(self):
        pass

    def increment_range(self):
        self.set_range(self.get_state().range + 1)

    def decrement_range(self):
        self.set_range(self.get_state().range - 1)

    def set_range(self, range: int):
        range = max(min(range, MAX_INVERSION_RANGE), 0)
        self.get_state().range = range
        old_inversion = self.get_state().value
        self.get_state().value = max(min(old_inversion, range), -1*range)

        self.update_chord_engine()
        self.update_redux_value()
        self.update_redux_range()

    def increment(self):
        new_inversion = self.get_state().value + 1
        if abs(new_inversion) <= self.get_state().range:
            self.set_value(new_inversion)

    def decrement(self):
        new_inversion = self.get_state().value - 1
        if abs(new_inversion) <= self.get_state().range:
            self.set_value(new_inversion)

    def set_value(self, inversion):
        if (not self.get_state().locked) and inversion != self.get_state().value:
                range = self.get_state().range
                self.get_state().value = max(min(inversion, range), -1*range)
                self.update_chord_engine()
                self.update_redux_value()

    def set_analog_value(self, value):
        inversion = self.process_value(value)
        self.set_value(inversion)

    def toggle_lock(self):
        self.get_state().locked = not self.get_state().locked
        self.update_redux_locked()

    def process_value(self, raw_value):
        max_steps = self.get_state().range
        last_value = self.get_state().value

        # converts to an integer in the correct inversion range
        def get_value(x):
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


