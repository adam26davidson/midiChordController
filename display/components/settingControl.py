from redux import store
from ..displayConstants import FONTS, COLORS
from pyrsistent import thaw
from redux import store
from redux.actions import display as actions
import tkinter as tk
from .menuItem import MenuItem

class SettingControl(tk.Frame):

    font = FONTS["small"]

    bgColor = '#000000'
    color = COLORS['chordColorDim']

    def __init__(self, container, name):
        super().__init__(
            container, 
            highlightthickness=0, 
            relief="flat", 
            bg="#000000")

        self.settingLabel = tk.Label(self,
            text=name,
            bg=self.bgColor, 
            fg=self.color, 
            font=self.font)

        self.settingLabel.pack(side='top')
