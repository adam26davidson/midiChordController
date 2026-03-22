from __future__ import annotations

import logging
import tkinter as tk

from redux import get_music_engine_state, store

from ..display_constants import COLORS, FONTS

logger = logging.getLogger(__name__)


class SettingDisplay(tk.Frame):
    width: int = 300
    height: int = 50

    bg_color: str = "#000000"
    color: str = COLORS["chord"]
    inactive_color: str = COLORS["chordDim"]
    active_color: str = COLORS["root"]

    def __init__(self, master: tk.Misc | None = None) -> None:
        super().__init__(master, width=self.width, height=self.height,
                         highlightthickness=0, relief="flat", bg=self.bg_color, border=2, borderwidth=2)
        self.parent = master
        self.chord_engine_control: str = 'internal'
        self.internal_setting_name: str = 'Loading...'

        big_font = FONTS["big"]
        small_font = FONTS["small"]

        # setting dsiplay
        self.setting_frame = tk.Frame(self, bg=self.bg_color, width=self.width)
        self.setting_frame.pack(side="top", anchor="nw")
        tk.Label(self.setting_frame, text="Setting: ", fg=self.inactive_color, bg=self.bg_color, font=small_font).pack(side="left")
        self.setting = tk.Label(self.setting_frame, text="Loading...", bg=self.bg_color, fg=self.color, font=big_font)
        self.setting.pack(side="top", pady=(0, 0))

        self.pack(side="top", anchor="nw", padx=(20, 20), pady=20)

        self._dirty: bool = False
        store.subscribe(self.__handle_store_update)

    def __handle_store_update(self) -> None:
        self._dirty = True

    def check_state(self) -> None:
        if not self._dirty:
            return
        self._dirty = False
        state = get_music_engine_state()
        if state['chordEngineControl'] != self.chord_engine_control:
            self.chord_engine_control = state['chordEngineControl']
            self.set_chord_engine_control(state['chordEngineControl'])

    def set_chord_engine_control(self, name: str) -> None:
        if name == 'internal':
            self.set_setting(self.internal_setting_name)
        else:
            self.set_setting("External Control")

    def set_setting(self, name: str) -> None:
        if self.chord_engine_control == 'internal':
            self.internal_setting_name = name
        logger.debug("setting setting text to %s", name)
        self.setting.configure(text=name)
