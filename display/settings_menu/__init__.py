import tkinter as tk

from redux import store
from redux.actions import display as actions

from .menu_item import MenuItem


class SettingsMenuFrame(tk.Frame):

    config = {
        "PERFORM": {"relx": 0.5, "rely": 0.5},
        "MIDI": {"relx": 0.5, "rely": 0.2},
        "CHORD": {"relx": 0.5, "rely": 0.8},
        "STRUM": {"relx": 0.22, "rely": 0.5},
        "PATCHES": {"relx": 0.78, "rely": 0.5},
    }

    def __init__(self, container):
        super().__init__(
            container,
            highlightthickness=0,
            relief="flat",
            bg="#000000")

        self.buttons = {}

        for key in self.config:
            self.buttons[key] = MenuItem(self, key, self.get_button_handler(key))
            self.buttons[key].place(
                relx=self.config[key]['relx'],
                rely=self.config[key]['rely'],
                anchor='center')

        self.buttons['PERFORM'].focus_set()

        self.buttons['PATCHES'].configure(
            state = tk.DISABLED,

        )

        self.grid(row=0, column=0, sticky='nsew')

    def get_button_handler(self, frame):
        return lambda: store.dispatch(actions.change_active_frame(frame))
