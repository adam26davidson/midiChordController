from __future__ import annotations

import tkinter as tk
from typing import Callable

from ..display_constants import COLORS, FONTS


class MenuItem(tk.Button):

    height: int = 80
    width: int = 100
    border: int = 5

    inactive_color: str = COLORS['chord']
    active_color: str = COLORS['root']

    big_font: tuple[str, int] | tuple[str, int, str] = FONTS["big"]

    def __init__(self, container: tk.Misc, text: str, callback: Callable[[], None]) -> None:
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
