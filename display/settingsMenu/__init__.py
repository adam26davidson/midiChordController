from redux import store
from pyrsistent import thaw
import tkinter as tk
from .menuItem import MenuItem

class SettingsMenuFrame(tk.Frame):

    height = 480
    width = 800

    def __init__(self, container):
        super().__init__(
            container, 
            highlightthickness=0, 
            relief="flat", 
            bg="#000000")

        self.performButton = MenuItem(self, "PERFORM")
        self.performButton.place(relx=0.5, rely=0.5, anchor='center')

        self.midiButton = MenuItem(self, "MIDI SETTINGS")
        self.midiButton.place(relx=0.5, rely=0.2, anchor='center')

        self.grid(row=0, column=0, sticky='nsew')
