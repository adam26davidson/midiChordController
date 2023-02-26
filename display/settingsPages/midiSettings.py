from ..components.numberPicker import NumberPicker
from ..components.buttonGroup import ButtonGroup
from ..components.settingsPage import SettingsPage
from ..components.slider import Slider
from ..components.settingsContainer import SettingsContainer
from redux import store
from redux.actions import musicEngine as meActions
from redux.settingsStorage import settingsStorageUtility
from pyrsistent import thaw
from redux import store
from redux.actions import display as actions
import tkinter as tk

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
            callback=self.setBassChannel)

        self.chordChannel = NumberPicker(self.channelFrame, 
            name='chord ch', 
            min=1, 
            max=16, 
            value=1,
            callback=self.setChordChannel)

        self.distributeChannels = ButtonGroup(self.channelFrame, 
            name='distribute channels',
            optionsList=[{'name': 'YES', 'value': True}, {'name': 'NO', 'value': False}],
            selected='NO',
            callback=self.setDistributeChannels)

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
            callback=self.setVelocityMode)

        self.aftertouchMode = ButtonGroup(self.velocityLeftFrame,
            name='aftertouch mode',
            optionsList=[{'name': 'CHAN', 'value': 'channel'}, {'name': 'POLY', 'value': 'poly'}],
            selected='CHAN',
            callback=self.setAftertouchMode)
        
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
            callback=self.setVelocityDeviation)

        
        self.velocityMode.pack(side='top', anchor="nw", pady=(5, 5), padx=(5, 5))
        self.aftertouchMode.pack(side='top', anchor="nw", pady=(5, 5), padx=(5, 5))
        self.velocityLeftFrame.pack(side='left', anchor="nw")

        self.velocity.pack(side='top', anchor="nw", pady=(5, 5), padx=(5, 5))
        self.velocityDeviation.pack(side='top', anchor="nw", pady=(5, 5), padx=(5, 5))
        self.slidersFrame.pack(side='left', anchor="nw")
        
        self.velocityFrame.grid(row=2, column=0, sticky='new', padx=(5, 5))

        store.subscribe(self.__handleStoreUpdate)


    def __handleStoreUpdate(self):
        state = store.get_state()
        meState = thaw(state['musicEngine'])

        if meState['velocity'] != self.velocity.getValue():
            self.velocity.setValue(meState['velocity'])
        if meState['velocityMode'] != self.velocityMode.getValue():
            self.velocityMode.setValue(meState['velocityMode'])
        if meState['velocityDeviation'] != self.velocityDeviation.getValue():
            self.velocityDeviation.setValue(meState['velocityDeviation'])
        if meState['chordChannel'] != (self.chordChannel.getValue() - 1):
            self.chordChannel.setValue(meState['chordChannel'] + 1)
        if meState['bassChannel'] != (self.bassChannel.getValue() - 1):
            self.bassChannel.setValue(meState['bassChannel'] + 1)
        if meState['distributeChannels'] != self.distributeChannels.getValue():
            self.distributeChannels.setValue(meState['distributeChannels'])
        if meState['aftertouchMode'] != self.aftertouchMode.getValue():
            self.aftertouchMode.setValue(meState['aftertouchMode'])
        

    def setBassChannel(self, channel):
        store.dispatch(meActions.changeBassChannel(channel - 1))
        settingsStorageUtility.saveSettings()

    def setChordChannel(self, channel):
        store.dispatch(meActions.changeChordChannel(channel - 1))
        settingsStorageUtility.saveSettings()
    
    def setDistributeChannels(self, value):
        store.dispatch(meActions.changeDistributeChannels(value))
        if (value):
            self.chordChannel.setDisabled()
        else:
            self.chordChannel.setEnabled()
        settingsStorageUtility.saveSettings()
    
    def setVelocityMode(self, mode):
        if mode == 'constant':
            self.velocityDeviation.setDisabled()
        if mode == 'random':
            self.velocityDeviation.setEnabled()
        store.dispatch(meActions.changeVelocityMode(mode))
        settingsStorageUtility.saveSettings()
    
    def setVelocity(self, velocity):
        store.dispatch(meActions.changeVelocity(velocity))
        settingsStorageUtility.saveSettings()
    
    def setVelocityDeviation(self, deviation):
        store.dispatch(meActions.changeVelocityDeviation(deviation))
        settingsStorageUtility.saveSettings()

    def setAftertouchMode(self, mode):
        store.dispatch(meActions.changeAftertouchMode(mode))
        settingsStorageUtility.saveSettings()
