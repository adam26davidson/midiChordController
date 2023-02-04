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

    def __init__(self, container, text):
        super().__init__(
            container, 
            width=10,
            height=3,
            highlightthickness=self.border,
            highlightcolor=self.activeColor,
            relief="flat",
            background="#000000",
            activebackground=self.activeColor,
            borderwidth=self.border,
            foreground=self.inactiveColor,
            activeforeground="#000000",
            font=self.bigFont,
            text=text)
        
