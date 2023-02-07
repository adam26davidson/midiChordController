from redux import store
from ..displayConstants import FONTS, COLORS
from .settingControl import SettingControl
from pyrsistent import thaw
from redux import store
from redux.actions import display as actions
import tkinter as tk

class Slider(SettingControl):

    def __init__(self, container, name, min, max, callback):
        super().__init__(container, name)

        self.max = max
        self.min = min
        self.callback = callback

        self.state = SliderState(self.min)

        self.contentsFrame = tk.Frame(self, 
            highlightthickness=0, 
            relief="flat", 
            bg="#000000")

        self.number = tk.Label(self.contentsFrame, 
            textvariable=self.state.number
            bg='#000000', 
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
            variable=self.state.number
            )
        
        self.number.pack(side='left')
        self.slider.pack(side='left')
        self.contentsFrame.pack(side='top', anchor='nw', padx=(2, 2), pady=(2, 2))

    def update()

    # def setDisabled(self):
    #     self.rightButton.setDisabled()
    #     self.leftButton.setDisabled()
    #     self.number.configure(fg=COLORS['chordDim'])
    
    # def setEnabled(self):
    #     self.rightButton.setEnabled()
    #     self.leftButton.setEnabled()
    #     self.number.configure(fg=COLORS['chord'])


class SliderState():
    disabled = False
    number = tk.IntVar()

    def __init__(self, number):
        self.number.set(number)