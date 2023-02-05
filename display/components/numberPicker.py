from redux import store
from ..displayConstants import FONTS, COLORS
from .settingControl import SettingControl
from pyrsistent import thaw
from redux import store
from redux.actions import display as actions
import tkinter as tk

class NumberPicker(SettingControl):

    mediumFont = FONTS["medium"]

    bgColor = '#000000'
    color = COLORS['chord']
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
            bg=self.bgColor, 
            fg=self.color, 
            font=self.mediumFont)
        
        self.rightButton = tk.Button(self.contentsFrame, 
            relief="flat",
            bg="#000000",
            bd=0,
            activebackground=self.activeColor,
            fg=self.color,
            activeforeground="#000000",
            font=self.mediumFont,
            text='>')
    
        self.leftButton = tk.Button(self.contentsFrame, 
            relief="flat",
            bg="#000000",
            bd=0,
            activebackground=self.activeColor,
            fg=self.color,
            activeforeground="#000000",
            font=self.mediumFont,
            text='<')
        
        self.leftButton.pack(side='left')
        self.number.pack(side='left')
        self.rightButton.pack(side='left')
        self.contentsFrame.pack(side='top')


class NumberPickerState():
    disabled = False
    number = 0
