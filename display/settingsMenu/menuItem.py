import tkinter as tk

from ..displayConstants import COLORS, FONTS


class MenuItem(tk.Button):

    height = 80
    width = 100
    border = 5

    inactive_color = COLORS['chord']
    active_color = COLORS['root']

    big_font = FONTS["big"]

    def __init__(self, container, text, callback):
        super().__init__(
            container,
            width=12,
            height=4,
            highlightthickness=self.border,
            highlightcolor=self.active_color,
            highlightbackground="#000000",
            relief="flat",
            background="#000000",
            disabledforeground=COLORS['chordDim'],
            bd=self.border,
            activebackground="#000000",
            foreground=self.inactive_color,
            activeforeground=self.inactive_color,
            font=self.big_font,
            text=text,
            command=callback)

