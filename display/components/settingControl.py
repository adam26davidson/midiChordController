import tkinter as tk

from ..displayConstants import COLORS, FONTS


class SettingControl(tk.Frame):

    def __init__(self, container, name):
        super().__init__(
            container,
            highlightthickness=0,
            relief="flat",
            bg="#000000")

        self.setting_label = tk.Label(self,
            text=name,
            bg='#000000',
            fg=COLORS['chordDim'],
            font=FONTS["medium"])

        self.setting_label.pack(side='top', anchor="nw")
