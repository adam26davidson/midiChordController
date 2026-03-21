import tkinter as tk

from ..display_constants import COLORS, FONTS
from .setting_control import SettingControl


class Slider(SettingControl):

    def __init__(self, container, name, min, max, value, callback, resolution=1, digits=0):
        super().__init__(container, name)

        self.max = max
        self.min = min
        self.callback = callback

        self.state = SliderState(self, value)

        self.contents_frame = tk.Frame(self,
            highlightthickness=0,
            relief="flat",
            bg="#000000")

        self.number = tk.Label(self.contents_frame,
            textvariable=self.state.number,
            bg='#000000',
            width=4,
            fg=COLORS['root'],
            font=FONTS["big"],
            )

        self.slider = tk.Scale(self.contents_frame,
            length=500,
            bd=0,
            from_=self.min,
            to=self.max,
            resolution=resolution,
            digits=digits,
            bg=COLORS['root'],
            orient='horizontal',
            troughcolor=COLORS['darkGrey'],
            width=50,
            sliderlength=50,
            sliderrelief='flat',
            font=FONTS['big'],
            fg=COLORS['root'],
            relief='flat',
            highlightthickness=0,
            activebackground=COLORS['root'],
            showvalue=False,
            variable=self.state.number,
            command=self.slider_callback)

        self.number.pack(side='left', pady=(4, 4), padx=(4, 4))
        self.slider.pack(side='left', pady=(4, 4), padx=(4, 4))
        self.contents_frame.pack(side='top', anchor='nw', padx=(2, 2), pady=(5, 5))

    def slider_callback(self, value):
        self.callback(float(value))

    def set_disabled(self):
        self.slider.configure(state=tk.DISABLED, bg=COLORS['chordDim'])
        self.number.configure(fg=COLORS['chordDim'])

    def set_enabled(self):
        self.slider.configure(state=tk.NORMAL, bg=COLORS['root'])
        self.number.configure(fg=COLORS['root'])

    def set_value(self, value):
        self.state.number.set(float(value))

    def get_value(self):
        return self.state.number.get()


class SliderState:
    disabled = False

    def __init__(self, container, number):
        self.number: tk.DoubleVar = tk.DoubleVar(container, value=float(number))
