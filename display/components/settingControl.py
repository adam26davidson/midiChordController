from redux import store
from ..displayConstants import FONTS, COLORS
from pyrsistent import thaw
from redux import store
from redux.actions import display as actions
import tkinter as tk

class SettingControl(tk.Frame):

    def __init__(self, container, name):
        super().__init__(
            container, 
            highlightthickness=0, 
            relief="flat", 
            bg="#000000")

        self.settingLabel = tk.Label(self,
            text=name,
            bg='#000000', 
            fg=COLORS['chordDim'], 
            font=FONTS["medium"])

        self.settingLabel.pack(side='top', anchor="nw")
