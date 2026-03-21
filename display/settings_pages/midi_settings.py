from pyrsistent import thaw

from redux import store
from redux.actions import music_engine as me_actions
from redux.settings_storage import settings_storage_utility

from ..components.button_group import ButtonGroup
from ..components.number_picker import NumberPicker
from ..components.settings_container import SettingsContainer
from ..components.settings_page import SettingsPage
from ..components.slider import Slider


class MidiSettingsFrame(SettingsPage):

    def __init__(self, container):
        super().__init__(
            container, 'MIDI SETTINGS')

        self.channelFrame = SettingsContainer(self)

        self.bassChannel = NumberPicker(self.channelFrame,
            name='bass ch',
            min=1,
            max=16,
            value=1,
            callback=self.set_bass_channel)

        self.chordChannel = NumberPicker(self.channelFrame,
            name='chord ch',
            min=1,
            max=16,
            value=1,
            callback=self.set_chord_channel)

        self.distributeChannels = ButtonGroup(self.channelFrame,
            name='distribute channels',
            optionsList=[{'name': 'YES', 'value': True}, {'name': 'NO', 'value': False}],
            selected='NO',
            callback=self.set_distribute_channels)

        self.distributeChannels.pack(side='left', anchor="nw", pady=(5, 5), padx=(5, 5))
        self.chordChannel.pack(side='left', anchor="nw", pady=(5, 5), padx=(5, 5))
        self.bassChannel.pack(side='left', anchor="nw", pady=(5, 5), padx=(5, 5))

        self.channelFrame.grid(row=1, column=0, sticky='new', padx=(5, 5))

        self.velocityFrame = SettingsContainer(self)

        self.velocityLeftFrame = SettingsContainer(self.velocityFrame)

        self.velocityMode = ButtonGroup(self.velocityLeftFrame,
            name='velocity mode',
            optionsList=[{'name': 'CONST', 'value': 'constant'}, {'name': 'RAND', 'value': 'random'}],
            selected='RAND',
            callback=self.set_velocity_mode)

        self.aftertouchMode = ButtonGroup(self.velocityLeftFrame,
            name='aftertouch mode',
            optionsList=[{'name': 'CHAN', 'value': 'channel'}, {'name': 'POLY', 'value': 'poly'}],
            selected='CHAN',
            callback=self.set_aftertouch_mode)

        self.slidersFrame = SettingsContainer(self.velocityFrame)

        self.velocity = Slider(self.slidersFrame,
            name='velocity',
            min=0,
            max=127,
            value=100,
            callback=self.setVelocity)

        self.velocityDeviation = Slider(self.slidersFrame,
            name='velocity deviation',
            min=0,
            max=64,
            value=10,
            callback=self.set_velocity_deviation)


        self.velocityMode.pack(side='top', anchor="nw", pady=(5, 5), padx=(5, 5))
        self.aftertouchMode.pack(side='top', anchor="nw", pady=(5, 5), padx=(5, 5))
        self.velocityLeftFrame.pack(side='left', anchor="nw")

        self.velocity.pack(side='top', anchor="nw", pady=(5, 5), padx=(5, 5))
        self.velocityDeviation.pack(side='top', anchor="nw", pady=(5, 5), padx=(5, 5))
        self.slidersFrame.pack(side='left', anchor="nw")

        self.velocityFrame.grid(row=2, column=0, sticky='new', padx=(5, 5))

        store.subscribe(self.__handle_store_update)


    def __handle_store_update(self):
        state = store.get_state()
        me_state = thaw(state['musicEngine'])

        if me_state['velocity'] != self.velocity.get_value():
            self.after(0, self.velocity.set_value(me_state['velocity']))
        if me_state['velocityMode'] != self.velocityMode.get_value():
            self.after(0, self.velocityMode.set_value(me_state['velocityMode']))
        if me_state['velocityDeviation'] != self.velocityDeviation.get_value():
            self.after(0, self.velocityDeviation.set_value(me_state['velocityDeviation']))
        if me_state['chordChannel'] != (self.chordChannel.get_value() - 1):
            self.after(0, self.chordChannel.set_value(me_state['chordChannel'] + 1))
        if me_state['bassChannel'] != (self.bassChannel.get_value() - 1):
            self.after(0, self.bassChannel.set_value(me_state['bassChannel'] + 1))
        if me_state['distributeChannels'] != self.distributeChannels.get_value():
            self.after(0, self.distributeChannels.set_value(me_state['distributeChannels']))
        if me_state['aftertouchMode'] != self.aftertouchMode.get_value():
            self.after(0, self.aftertouchMode.set_value(me_state['aftertouchMode']))


    def set_bass_channel(self, channel):
        store.dispatch(me_actions.change_bass_channel(channel - 1))
        settings_storage_utility.save_settings()

    def set_chord_channel(self, channel):
        store.dispatch(me_actions.change_chord_channel(channel - 1))
        settings_storage_utility.save_settings()

    def set_distribute_channels(self, value):
        store.dispatch(me_actions.change_distribute_channels(value))
        if (value):
            self.chordChannel.set_disabled()
        else:
            self.chordChannel.set_enabled()
        settings_storage_utility.save_settings()

    def set_velocity_mode(self, mode):
        if mode == 'constant':
            self.velocityDeviation.set_disabled()
        if mode == 'random':
            self.velocityDeviation.set_enabled()
        store.dispatch(me_actions.change_velocity_mode(mode))
        settings_storage_utility.save_settings()

    def set_velocity(self, velocity):
        store.dispatch(me_actions.change_velocity(velocity))
        settings_storage_utility.save_settings()

    def set_velocity_deviation(self, deviation):
        store.dispatch(me_actions.change_velocity_deviation(deviation))
        settings_storage_utility.save_settings()

    def set_aftertouch_mode(self, mode):
        store.dispatch(me_actions.change_aftertouch_mode(mode))
        settings_storage_utility.save_settings()
