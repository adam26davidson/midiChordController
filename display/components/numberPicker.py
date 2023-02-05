from redux import store
from ..displayConstants import FONTS, COLORS
from .settingControl import SettingControl
from pyrsistent import thaw
from redux import store
from redux.actions import display as actions
import tkinter as tk

class NumberPicker(SettingControl):

    def __init__(self, container, name):
        super().__init__(container, name)

        self.state = NumberPickerState()

        self.contentsFrame = tk.Frame(self, 
            highlightthickness=0, 
            relief="flat", 
            bg="#000000")

        self.number = tk.Label(self.contentsFrame, 
            text=self.state.number,
            bg='#000000', 
            fg=COLORS['chord'], 
            font=FONTS["big"])
        
        self.rightButton = ArrowButton(self.contentsFrame, 'right')
        self.leftButton = ArrowButton(self.contentsFrame, 'left')
        
        self.leftButton.pack(side='left', padx=(3, 3), pady=(3, 5))
        self.number.pack(side='left', padx=(2, 2), pady=(3, 3))
        self.rightButton.pack(side='left', padx=(3, 3), pady=(3, 5))
        self.contentsFrame.pack(side='top', anchor='nw', padx=(2, 2), pady=(2, 2))

class ArrowButton(tk.Button):

    def __init__(self, container, side):
        text = '\u25B6'
        if side == 'left':
            text = '\u25C0'

        super().__init__(container,
            highlightthickness=0, 
            relief="flat",
            bg="#000000",
            height=2,
            width=2,
            bd=0,
            activebackground=COLORS['root'],
            fg=COLORS['chord'],
            activeforeground="#000000",
            font=FONTS["big"],
            text=text)

class NumberPickerState():
    disabled = False
    number = 0
