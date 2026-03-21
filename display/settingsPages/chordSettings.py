from pyrsistent import thaw

from constants import MAX_BASS_RANGE, MAX_INVERSION_RANGE
from redux import store
from redux.actions import musicEngine as meActions
from redux.settingsStorage import settings_storage_utility

from ..components.buttonGroup import ButtonGroup
from ..components.numberPicker import NumberPicker
from ..components.settingsContainer import SettingsContainer
from ..components.settingsPage import SettingsPage


class ChordSettingsFrame(SettingsPage):

    def __init__(self, container):
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
            optionsList=[{'name': 'INT', 'value': 'internal'}, {'name': 'EXT', 'value': 'external'}],
            selected='INT',
            callback=self.set_control_mode)

        self.controlMode.pack(side='left', anchor="nw", pady=(5, 5), padx=(5, 5))
        self.rowTwo.grid(row=2, column=0, sticky='new', padx=(5, 5))

        store.subscribe(self.__handle_store_update)


    def __handle_store_update(self):
        me_state = thaw(store.get_state()['musicEngine'])

        if me_state['transposeIncrement'] != self.transposeIncrement.get_value():
            self.after(0, self.transposeIncrement.set_value(me_state['transposeIncrement']))
        if me_state['inversionRange'] != self.inversionRange.get_value():
            self.after(0, self.inversionRange.set_value(me_state['inversionRange']))
        if me_state['bassRange'] != self.bassRange.get_value():
            self.after(0, self.bassRange.set_value(me_state['bassRange']))
        if me_state['chordEngineControl'] != self.controlMode.get_value():
            self.after(0, self.controlMode.set_value(me_state['chordEngineControl']))

    def set_transpose_increment(self, increment):
        store.dispatch(meActions.change_transpose_increment(increment))
        settings_storage_utility.save_settings()

    def set_inversion_range(self, range):
        store.dispatch(meActions.change_inversion_range(range))
        settings_storage_utility.save_settings()

    def set_bass_range(self, range):
        store.dispatch(meActions.change_bass_range(range))
        settings_storage_utility.save_settings()

    def set_control_mode(self, mode):
        store.dispatch(meActions.change_chord_engine_control(mode))
        settings_storage_utility.save_settings()
