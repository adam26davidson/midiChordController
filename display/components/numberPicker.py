import tkinter as tk

from ..displayConstants import COLORS, FONTS
from .settingControl import SettingControl


class NumberPicker(SettingControl):

    def __init__(self, container, name, min, max, value, callback):
        super().__init__(container, name)

        self.max = max
        self.min = min
        self.callback = callback

        self.state = NumberPickerState(value)

        self.contents_frame = tk.Frame(self,
            highlightthickness=0,
            relief="flat",
            bg="#000000")

        self.number = tk.Label(self.contents_frame,
            text=self.state.number,
            width=2,
            bg='#000000',
            fg=COLORS['root'],
            font=FONTS["big"])

        self.right_button = ArrowButton(self.contents_frame, 'right', self.increment_number)
        self.left_button = ArrowButton(self.contents_frame, 'left', self.decrement_number)

        self.left_button.pack(side='left', padx=(3, 3), pady=(3, 6))
        self.number.pack(side='left', padx=(3, 3), pady=(3, 3))
        self.right_button.pack(side='left', padx=(3, 3), pady=(3, 6))
        self.contents_frame.pack(side='top', anchor='nw', padx=(2, 2), pady=(2, 2))

    def increment_number(self):
        if self.state.number + 1 <= self.max:
            self.state.number += 1
        else:
            self.state.number = self.min

        self.number.configure(text=str(self.state.number))
        self.callback(self.state.number)

    def decrement_number(self):
        if self.state.number - 1 >= self.min:
            self.state.number -= 1
        else:
            self.state.number = self.max

        self.number.configure(text=str(self.state.number))
        self.callback(self.state.number)

    def set_disabled(self):
        self.right_button.set_disabled()
        self.left_button.set_disabled()
        self.number.configure(fg=COLORS['chordDim'])

    def set_enabled(self):
        self.right_button.set_enabled()
        self.left_button.set_enabled()
        self.number.configure(fg=COLORS['chord'])

    def set_value(self, value):
        self.state.number = value
        self.number.configure(text=str(self.state.number))

    def get_value(self):
        return self.state.number


class ArrowButton(tk.Button):

    def __init__(self, container, side, callback):
        text = '\u25B6'
        if side == 'left':
            text = '\u25C0'

        super().__init__(container,
            highlightthickness=0,
            relief="flat",
            bg="#000000",
            height=2,
            width=3,
            bd=0,
            activebackground="#000000",
            fg=COLORS['chordDim'],
            activeforeground=COLORS['chordDim'],
            font=FONTS["biggest"],
            disabledforeground=COLORS['chordDim'],
            text=text,
            command=callback)

    def set_disabled(self):
        self.configure(state=tk.DISABLED)

    def set_enabled(self):
        self.configure(state=tk.NORMAL)


class NumberPickerState:
    disabled = False
    number = 0

    def __init__(self, number):
        self.number = number
