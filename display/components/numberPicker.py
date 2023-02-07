from redux import store
from ..displayConstants import FONTS, COLORS
from .settingControl import SettingControl
from pyrsistent import thaw
from redux import store
from redux.actions import display as actions
import tkinter as tk

class NumberPicker(SettingControl):

    def __init__(self, container, name, min, max, callback):
        super().__init__(container, name)

        self.max = max
        self.min = min
        self.callback = callback

        self.state = NumberPickerState(self.min)

        self.contentsFrame = tk.Frame(self, 
            highlightthickness=0, 
            relief="flat", 
            bg="#000000")

        self.number = tk.Label(self.contentsFrame, 
            text=self.state.number,
            bg='#000000', 
            fg=COLORS['root'], 
            font=FONTS["big"])
        
        self.rightButton = ArrowButton(self.contentsFrame, 'right', self.incrementNumber)
        self.leftButton = ArrowButton(self.contentsFrame, 'left', self.decrementNumber)
        
        self.leftButton.pack(side='left', padx=(3, 3), pady=(3, 6))
        self.number.pack(side='left', padx=(4, 4), pady=(3, 3))
        self.rightButton.pack(side='left', padx=(3, 3), pady=(3, 6))
        self.contentsFrame.pack(side='top', anchor='nw', padx=(2, 2), pady=(2, 2))

    def incrementNumber(self):
        if self.state.number + 1 <= self.max:
            self.state.number += 1
        else:
            self.state.number = self.min

        self.number.configure(text=str(self.state.number))
        self.callback(self.state.number)

    def decrementNumber(self):
        if self.state.number - 1 >= self.min:
            self.state.number -= 1
        else:
            self.state.number = self.max

        self.number.configure(text=str(self.state.number))
        self.callback(self.state.number)

    def setDisabled(self):
        self.rightButton.setDisabled()
        self.leftButton.setDisabled()
        self.number.configure(fg=COLORS['chordDim'])
    
    def setEnabled(self):
        self.rightButton.setEnabled()
        self.leftButton.setEnabled()
        self.number.configure(fg=COLORS['chord'])
        

class ArrowButton(tk.Button):

    def __init__(self, container, side, callback):
        text = '\u25B6'
        if side == 'left':
            text = '\u25C0'

        super().__init__(container,
            highlightthickness=0, 
            relief="flat",
            bg="#000000",
            height=3,
            width=3,
            bd=0,
            activebackground="#000000",
            fg=COLORS['chord'],
            activeforeground=COLORS['root'],
            font=FONTS["big"],
            disabledforeground=COLORS['chordDim'],
            text=text,
            command=callback)

    def setDisabled(self):
        self.configure(state=tk.DISABLED)
    
    def setEnabled(self):
        self.configure(state=tk.NORMAL)


class NumberPickerState():
    disabled = False
    number = 0

    def __init__(self, number):
        self.number = number
