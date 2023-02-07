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

        self.slider = tk.Scale(self.contentsFrame, 
            length=500,
            bd=0,
            from_=self.min,
            to=self.max,
            bg="#000000",
            orient='horizontal',
            troughcolor=COLORS['darkGrey'],
            width=40,
            sliderlength=50,
            sliderrelief='flat',
            font=FONTS['big'],
            fg=COLORS['root'],
            relief='flat',
            highlightthickness=0,
            activebackground=COLORS['root']
            )
        for slave in self.slider.slaves:
            print(slave.winfo_width())
        
        self.slider.pack(side='left')
        self.contentsFrame.pack(side='top', anchor='nw', padx=(2, 2), pady=(2, 2))


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
    number = 0

    def __init__(self, number):
        self.number = number