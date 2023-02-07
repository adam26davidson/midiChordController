from ..components.numberPicker import NumberPicker
from ..components.buttonGroup import ButtonGroup
from ..components.settingsPage import SettingsPage
from ..components.slider import Slider
from redux import store
from redux.actions import musicEngine as meActions
from pyrsistent import thaw
from redux import store
from redux.actions import display as actions
import tkinter as tk

class MidiSettingsFrame(SettingsPage):

    def __init__(self, container):
        super().__init__(
            container, 'MIDI SETTINGS')
        
        self.state = MidiSetingsState()

        self.channelFrame = tk.Frame(self, 
            highlightthickness=0, 
            relief="flat", 
            bg="#000000")

        self.bassChannel = NumberPicker(self.channelFrame, name='bass ch', min=1, max=16, callback=self.setBassChannel)
        self.chordChannel = NumberPicker(self.channelFrame, name='chord ch', min=1, max=16, callback=self.setChordChannel)
        self.distributeChannels = ButtonGroup(self.channelFrame, 
            name='distribute channels',
            optionsList=[{'name': 'YES', 'value': True}, {'name': 'NO', 'value': False}],
            selected='NO',
            callback=self.setDistributeChannels)

        self.chordChannel.pack(side='left', anchor="nw")
        self.bassChannel.pack(side='left', anchor="nw")
        self.distributeChannels.pack(side='left', anchor="nw")

        self.channelFrame.grid(row=1, column=0, sticky='new', padx=(5, 5))

        self.velocityFrame = tk.Frame(self, 
            highlightthickness=0, 
            relief="flat", 
            bg="#000000")
        
        self.velocityMode = ButtonGroup(self.velocityFrame,
            name='velocity mode',
            optionsList=[{'name': 'CONST', 'value': 'constant'}, {'name': 'RAND', 'value': 'random'}],
            selected='CONST',
            callback=self.setVelocityMode)

        self.velocity = Slider(self.velocityFrame, 
            name='velocity',
            min=0,
            max=127,
            value=100,
            callback=self.setVelocity)
        
        self.velocityDeviation = Slider(self.velocityFrame, 
            name='velocity deviation',
            min=0,
            max=64,
            value=10,
            callback=self.setVelocityDeviation)

        self.velocityMode.pack(side='left', anchor="nw")
        self.velocity.pack(side='left', anchor="nw")
        self.velocityDeviation.pack(side='left', anchor="nw")

        self.velocityFrame.grid(row=2, column=0, sticky='new', padx=(5, 5))


    def setBassChannel(self, channel):
        store.dispatch(meActions.changeBassChannel(channel - 1))

    def setChordChannel(self, channel):
        store.dispatch(meActions.changeChordChannel(channel - 1))
    
    def setDistributeChannels(self, value):
        store.dispatch(meActions.changeDistributeChannels(value))
        if (value):
            self.chordChannel.setDisabled()
            self.bassChannel.setDisabled()
        else:
            self.chordChannel.setEnabled()
            self.chordChannel.setEnabled()
    
    def setVelocityMode(self, mode):
        if mode == 'constant':
            self.velocityDeviation.setDisabled()
        if mode == 'random':
            self.velocityDeviation.setEnabled()
        store.dispatch(meActions.changeVelocityMode(mode))
    
    def setVelocity(self, velocity):
        store.dispatch(meActions.changeVelocity(velocity))
    
    def setVelocityDeviation(self, deviation):
        store.dispatch(meActions.changeVelocityDeviation(deviation))

class MidiSetingsState():
    distributeChannels = False