from ..components.numberPicker import NumberPicker
from redux import store
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
        
        self.bassChannel = NumberPicker(self, 'bass channel')
        self.chordChannel = NumberPicker(self, 'chord channel')

        self.chordChannel.pack(side='left', anchor="nw")
        self.bassChannel.pack(side='left', anchor="nw")

        self.grid(row=0, column=0, sticky='nsew')


