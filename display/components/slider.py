from redux import store
from ..displayConstants import FONTS, COLORS
from .settingControl import SettingControl
from pyrsistent import thaw
from redux import store
from redux.actions import display as actions
import tkinter as tk

class Slider(SettingControl):

    def __init__(self, container, name, min, max, value, callback):
        super().__init__(container, name)

        self.max = max
        self.min = min
        self.callback = callback

        self.state = SliderState(self, value)

        self.contentsFrame = tk.Frame(self, 
            highlightthickness=0, 
            relief="flat", 
            bg="#000000")

        self.number = tk.Label(self.contentsFrame, 
            textvariable=self.state.number,
            bg='#000000', 
            width=3,
            fg=COLORS['root'], 
            font=FONTS["big"],
            )

        self.slider = tk.Scale(self.contentsFrame, 
            length=500,
            bd=0,
            from_=self.min,
            to=self.max,
            bg=COLORS['root'],
            orient='horizontal',
            troughcolor=COLORS['darkGrey'],
            width=40,
            sliderlength=50,
            sliderrelief='flat',
            font=FONTS['big'],
            fg=COLORS['root'],
            relief='flat',
            highlightthickness=0,
            activebackground=COLORS['root'],
            showvalue=False,
            variable=self.state.number,
            command=self.sliderCallback)
        
        self.number.pack(side='left', pady=(4, 4), padx=(4, 4))
        self.slider.pack(side='left', pady=(4, 4), padx=(4, 4))
        self.contentsFrame.pack(side='top', anchor='nw', padx=(2, 2), pady=(5, 5))

    def sliderCallback(self, value):
        self.callback(value)

    def setDisabled(self):
        self.slider.configure(state=tk.DISABLED, bg=COLORS['chordDim'])
        self.number.configure(fg=COLORS['chordDim'])
    
    def setEnabled(self):
        self.slider.configure(state=tk.NORMAL, bg=COLORS['root'])
        self.number.configure(fg=COLORS['root'])


class SliderState():
    disabled = False

    def __init__(self, container, number):
        self.number = tk.IntVar(container, value=number)