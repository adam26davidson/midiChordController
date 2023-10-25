from redux import store
from ..displayConstants import COLORS, FONTS
import tkinter as tk

class MenuItem(tk.Button):

    height = 80
    width = 100
    border = 5

    inactiveColor = COLORS['chord']
    activeColor = COLORS['root']

    bigFont = FONTS["big"]

    def __init__(self, container, text, callback):
        super().__init__(
            container, 
            width=12,
            height=4,
            highlightthickness=self.border,
            highlightcolor=self.activeColor,
            highlightbackground="#000000",
            relief="flat",
            background="#000000",
            disabledforeground=COLORS['chordDim'],
            bd=self.border,
            activebackground="#000000",
            foreground=self.inactiveColor,
            activeforeground=self.inactiveColor,
            font=self.bigFont,
            text=text,
            command=callback)
        
