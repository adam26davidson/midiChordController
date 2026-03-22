from __future__ import annotations

import tkinter as tk

from ..display_constants import COLORS, FONTS


class SettingControl(tk.Frame):

    def __init__(self, container: tk.Misc, name: str) -> None:
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
