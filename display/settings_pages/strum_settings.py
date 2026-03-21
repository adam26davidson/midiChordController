from redux import store
from redux.actions import music_engine as me_actions
from redux.settings_storage import settings_storage_utility

from ..components.button_group import ButtonGroup
from ..components.settings_container import SettingsContainer
from ..components.settings_page import SettingsPage
from ..components.slider import Slider


class StrumSettingsFrame(SettingsPage):

    def __init__(self, container):
        super().__init__(
            container, 'STRUM SETTINGS')

        self.topFrame = SettingsContainer(self)
        self.bottomFrame = SettingsContainer(self)

        self.strumMode = ButtonGroup(self.topFrame,
            name='strum mode',
            options_list=[
                {'name': 'RAND', 'value': 'random'},
                {'name': 'REG', 'value': 'regular'},
                {'name': 'OFF', 'value': 'off'},
            ],
            selected='REG',
            callback=self.set_strum_mode)

        self.strumOrder = ButtonGroup(self.topFrame,
            name='strum order',
            options_list=[
                {'name': 'UP', 'value': 'up'},
                {'name': 'DOWN', 'value': 'down'},
                {'name': 'RAND', 'value': 'random'},
            ],
            selected='RAND',
            callback=self.set_strum_order)

        self.strumInterval = Slider(self.bottomFrame,
            name='strum interval',
            min=0,
            max=1,
            resolution=0.005,
            digits=4,
            value=0.02,
            callback=self.set_strum_interval)

        self.strumMode.pack(side='left', anchor="nw", pady=(5, 5), padx=(5, 5))
        self.strumOrder.pack(side='left', anchor="nw", pady=(5, 5), padx=(5, 5))
        self.topFrame.grid(row=1, column=0, sticky='new', padx=(5, 5))

        self.strumInterval.pack(side='left', anchor="nw", pady=(5, 5), padx=(5, 5))
        self.bottomFrame.grid(row=2, column=0, sticky='new', padx=(5, 5))

        self._dirty = False
        store.subscribe(self.__handle_store_update)

    def __handle_store_update(self):
        self._dirty = True

    def check_state(self):
        if not self._dirty:
            return
        self._dirty = False
        me_state = store.get_state()['musicEngine']

        if me_state['strumMode'] != self.strumMode.get_value():
            self.strumMode.set_value(me_state['strumMode'])
        if me_state['strumInterval'] != self.strumInterval.get_value():
            self.strumInterval.set_value(me_state['strumInterval'])
        if me_state['strumOrder'] != self.strumOrder.get_value():
            self.strumOrder.set_value(me_state['strumOrder'])

    def set_strum_mode(self, mode):
        store.dispatch(me_actions.change_strum_mode(mode))
        settings_storage_utility.save_settings()
        if mode == 'off':
            self.strumInterval.set_disabled()
            self.strumOrder.set_disabled()
        else:
            self.strumInterval.set_enabled()
            self.strumOrder.set_enabled()

    def set_strum_interval(self, interval):
        store.dispatch(me_actions.change_strum_interval(interval))
        settings_storage_utility.save_settings()

    def set_strum_order(self, order):
        store.dispatch(me_actions.change_strum_order(order))
        settings_storage_utility.save_settings()
