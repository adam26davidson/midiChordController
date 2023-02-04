from redux import store
from ..displayConstants import COLORS, FONTS
import tkinter as tk

class MenuItem(tk.Button):

    height = 80
    width = 100
    border = 5

    inactiveColor = COLORS['chordDim']
    activeColor = COLORS['root']

    bigFont = FONTS["big"]

    def __init__(self, container, text):
        super().__init__(
            container, 
            height = self.height,
            width=self.width,
            highlightthickness=0, 
            relief="flat",
            background="#000000",
            borderwidth=self.border,
            foreground=self.activeColor,
            font=self.bigFont,
            text=text)
        
