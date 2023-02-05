from redux import store
from ..displayConstants import FONTS, COLORS
from .settingControl import SettingControl
from pyrsistent import thaw
from redux import store
from redux.actions import display as actions
import tkinter as tk

class NumberPicker(SettingControl):

    font = FONTS["big"]

    activeColor = COLORS['root']

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
            font=self.font)
        
        self.rightButton = tk.Button(self.contentsFrame, 
            highlightthickness=0, 
            relief="flat",
            bg="#000000",
            bd=0,
            activebackground=COLORS['root'],
            fg=COLORS['chord'],
            activeforeground="#000000",
            font=self.font,
            text='\u25B6')
    
        self.leftButton = tk.Button(self.contentsFrame, 
            highlightthickness=0,
            relief="flat",
            bg="#000000",
            bd=0,
            activebackground=COLORS['root'],
            fg=COLORS['chord'],
            activeforeground="#000000",
            font=self.font,
            text='\u25C0')
        
        self.leftButton.pack(side='left', padx=(3, 3), pady=(3, 3))
        self.number.pack(side='left', padx=(2, 2), pady=(3, 3))
        self.rightButton.pack(side='left', padx=(3, 3), pady=(3, 3))
        self.contentsFrame.pack(side='top', padx=(2, 2), pady=(2, 2))


class NumberPickerState():
    disabled = False
    number = 0
