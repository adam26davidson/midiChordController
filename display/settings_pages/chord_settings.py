from __future__ import annotations

from typing import TYPE_CHECKING

from constants import MAX_BASS_RANGE, MAX_INVERSION_RANGE
from redux import get_music_engine_state, store
from redux.actions import music_engine as me_actions
from redux.settings_storage import settings_storage_utility

from ..components.button_group import ButtonGroup
from ..components.number_picker import NumberPicker
from ..components.settings_container import SettingsContainer
from ..components.settings_page import SettingsPage

if TYPE_CHECKING:
    import tkinter as tk


class ChordSettingsFrame(SettingsPage):

    def __init__(self, container: tk.Misc) -> None:
        super().__init__(
            container, 'CHORD SETTINGS')

        self.rowOne = SettingsContainer(self)

        self.transposeIncrement = NumberPicker(self.rowOne,
            name='transpose increment',
            min=1,
            max=11,
            value=1,
            callback=self.set_transpose_increment)

        self.inversionRange = NumberPicker(self.rowOne,
            name='inversion range',
            min=1,
            max=MAX_INVERSION_RANGE,
            value=4,
            callback=self.set_inversion_range)

        self.bassRange = NumberPicker(self.rowOne,
            name='bass range',
            min=1,
            max=MAX_BASS_RANGE,
            value=4,
            callback=self.set_bass_range)

        self.transposeIncrement.pack(side='left', anchor="nw", pady=(5, 5), padx=(5, 5))
        self.inversionRange.pack(side='left', anchor="nw", pady=(5, 5), padx=(5, 5))
        self.bassRange.pack(side='left', anchor="nw", pady=(5, 5), padx=(5, 5))

        self.rowOne.grid(row=1, column=0, sticky='new', padx=(5, 5))

        self.rowTwo = SettingsContainer(self)

        self.controlMode = ButtonGroup(self.rowTwo,
            name='control mode',
            options_list=[{'name': 'INT', 'value': 'internal'}, {'name': 'EXT', 'value': 'external'}],
            selected='INT',
            callback=self.set_control_mode)

        self.controlMode.pack(side='left', anchor="nw", pady=(5, 5), padx=(5, 5))
        self.rowTwo.grid(row=2, column=0, sticky='new', padx=(5, 5))

        self._dirty: bool = False
        store.subscribe(self.__handle_store_update)

    def __handle_store_update(self) -> None:
        self._dirty = True

    def check_state(self) -> None:
        if not self._dirty:
            return
        self._dirty = False
        me_state = get_music_engine_state()

        if me_state['transposeIncrement'] != self.transposeIncrement.get_value():
            self.transposeIncrement.set_value(me_state['transposeIncrement'])
        if me_state['inversionRange'] != self.inversionRange.get_value():
            self.inversionRange.set_value(me_state['inversionRange'])
        if me_state['bassRange'] != self.bassRange.get_value():
            self.bassRange.set_value(me_state['bassRange'])
        if me_state['chordEngineControl'] != self.controlMode.get_value():
            self.controlMode.set_value(me_state['chordEngineControl'])

    def set_transpose_increment(self, increment: int) -> None:
        store.dispatch(me_actions.change_transpose_increment(increment))
        settings_storage_utility.save_settings()

    def set_inversion_range(self, range: int) -> None:
        store.dispatch(me_actions.change_inversion_range(range))
        settings_storage_utility.save_settings()

    def set_bass_range(self, range: int) -> None:
        store.dispatch(me_actions.change_bass_range(range))
        settings_storage_utility.save_settings()

    def set_control_mode(self, mode: str) -> None:
        store.dispatch(me_actions.change_chord_engine_control(mode))
        settings_storage_utility.save_settings()
