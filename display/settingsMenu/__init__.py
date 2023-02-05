from redux import store
from pyrsistent import thaw
from redux import store
from redux.actions import display as actions
import tkinter as tk
from .menuItem import MenuItem

class SettingsMenuFrame(tk.Frame):

    config = {
        "PERFROM": {"relx": 0.5, "rely": 0.5},
        "MIDI": {"relx": 0.5, "rely": 0.2},
        "CHORD": {"relx": 0.5, "rely": 0.8},
        "STRUM": {"relx": 0.22, "rely": 0.5},
        "PATCHES": {"relx": 0.78, "rely": 0.5},
    }

    def __init__(self, container):
        super().__init__(
            container, 
            highlightthickness=0, 
            relief="flat", 
            bg="#000000")
        
        self.buttons = {}

        for key in self.config.keys():
            self.buttons[key] = MenuItem(self, key, self.getButtonHandler(key))
            self.buttons[key].place(
                relx=self.config[key]['relx'], 
                rely=self.config[key]['rely'], 
                anchor='center')

        self.buttons['PERFROM'].focus_set()

        self.grid(row=0, column=0, sticky='nsew')

    def getButtonHandler(self, frame):
        return lambda: store.dispatch(actions.changeActiveFrame(frame))
