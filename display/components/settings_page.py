from __future__ import annotations

import tkinter as tk

from redux import store
from redux.actions import display as actions

from ..display_constants import COLORS, FONTS


class SettingsPage(tk.Frame):

    def __init__(self, container: tk.Misc, name: str) -> None:
        super().__init__(
            container,
            highlightthickness=0,
            relief="flat",
            bg="#000000")

        self.title_frame = tk.Frame(self,
            highlightthickness=0,
            relief="flat",
            bg="#000000",
            height=80,
            width=800)

        self.title = tk.Label(self.title_frame,
            text=name,
            bg='#000000',
            fg=COLORS['chord'],
            font=FONTS["big"],
            justify='center')

        self.menu_button = tk.Button(self.title_frame,
            highlightthickness=0,
            relief="flat",
            bg="#000000",
            height=2,
            width=7,
            bd=0,
            activebackground="#000000",
            fg=COLORS['chord'],
            activeforeground=COLORS['chord'],
            font=FONTS["big"],
            disabledforeground=COLORS['chordDim'],
            text='\u25C0 MENU',
            command=lambda: store.dispatch(actions.change_active_frame('MENU')))

        self.menu_button.place(rely=0.5, relx=0.08, anchor='center')
        self.title.place(rely=0.5, relx=0.5, anchor='center')
        self.title_frame.grid(row=0, column=0, sticky='new', )

        self.grid(row=0, column=0, sticky='nsew')
