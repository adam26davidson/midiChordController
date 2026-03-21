from typing import Callable

from pyrsistent import thaw

from constants import MAX_OCTAVE_SHIFT
from models.appParameter import AppParameter, AppParameterType
from models.command import Command
from models.commandType import CommandType
from redux import store
from redux import utils as redux_utils
from redux.actions import musicEngine as actions
from redux.settingsStorage import settings_storage_utility

from ..chordEngineState import state


class ChordOctave:

    update_chord_engine: Callable
    type: AppParameterType

    def __init__(self, type: AppParameterType, update_chord_engine: Callable):
        self.update_chord_engine = update_chord_engine
        self.type = type
        store.subscribe(self.__handle_store_update)
        store.dispatch(actions.change_chord_octave(state.chord_octave))

        redux_utils.add_app_parameters(self.__get_parameters())

    def __handle_store_update(self):
        me_state = thaw(store.get_state()['musicEngine'])
        if (me_state['chordOctave'] != state.chord_octave):
            self.set(me_state['chordOctave'])

    def apply(self, notes: list[int]) -> list[int]:
        return [note + (state.chord_octave * 12) for note in notes]

    def set(self, octave):
        clamped = max(min(octave, MAX_OCTAVE_SHIFT), -1*MAX_OCTAVE_SHIFT)
        state.chord_octave = clamped
        store.dispatch(actions.change_chord_octave(state.chord_octave))
        settings_storage_utility.save_settings()
        self.update_chord_engine()

    def increment(self):
        self.set(state.chord_octave + 1)

    def decrement(self):
        self.set(state.chord_octave - 1)

    def __get_parameters(self):
        key_prefix = "EXTERNAL_" if self.type == AppParameterType.EXTERNAL_CHORD_ENGINE else "INTERNAL_"
        return [
            AppParameter(
                valid_command_types = [CommandType.INCREMENTAL],
                command_mappings = {
                    Command.INCREMENT: self.increment,
                    Command.DECREMENT: self.decrement
                },
                key = f"{key_prefix}OCTAVE",
                label = "Octave",
                label_abreviation="O",
                type = self.type
            )
        ]
