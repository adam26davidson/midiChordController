from ..components.numberPicker import NumberPicker
from ..components.buttonGroup import ButtonGroup
from redux import store
from redux.actions import musicEngine as meActions
from pyrsistent import thaw
from redux import store
from redux.actions import display as actions
import tkinter as tk

class MidiSettingsFrame(tk.Frame):

    def __init__(self, container):
        super().__init__(
            container, 
            highlightthickness=0, 
            relief="flat", 
            bg="#000000")
        
        self.state = MidiSetingsState()
        
        self.bassChannel = NumberPicker(self, name='bass ch', min=1, max=16, callback=self.setBassChannel)
        self.chordChannel = NumberPicker(self, name='chord ch', min=1, max=16, callback=self.setChordChannel)
        self.distributeChannels = ButtonGroup(self, 
            name='distribute channels',
            optionsList=[{'name': 'YES', 'value': True}, {'name': 'NO', 'value': False}],
            callback=self.setDistributeChannels)

        self.chordChannel.pack(side='left', anchor="nw")
        self.bassChannel.pack(side='left', anchor="nw")

        self.grid(row=0, column=0, sticky='nsew')

    def setBassChannel(self, channel):
        store.dispatch(meActions.changeBassChannel(channel - 1))

    def setChordChannel(self, channel):
        store.dispatch(meActions.changeChordChannel(channel - 1))
    
    def setDistributeChannels(self, value):
        store.dispatch(meActions.changeDistributeChannels(value))

class MidiSetingsState():
    distributeChannels = False