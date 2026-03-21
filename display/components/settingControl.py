import tkinter as tk

from ..displayConstants import COLORS, FONTS


class SettingControl(tk.Frame):

    def __init__(self, container, name):
        super().__init__(
            container,
            highlightthickness=0,
            relief="flat",
            bg="#000000")

        self.settingLabel = tk.Label(self,
            text=name,
            bg='#000000',
            fg=COLORS['chordDim'],
            font=FONTS["medium"])

        self.settingLabel.pack(side='top', anchor="nw")
