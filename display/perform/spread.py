from __future__ import annotations

import tkinter as tk

from constants import SPREAD_STEPS_PER_OCTAVE
from redux import get_music_engine_state, store


class Spread(tk.Canvas):
    width: int = 720
    height: int = 30
    num_keys: int = 61
    color: str = "#828282"

    def __init__(self, master: tk.Misc | None = None) -> None:
        super().__init__(master, width=self.width, height=self.height,
                         highlightthickness=0, relief="flat", bg="#000000")
        self.state: dict[str, float] = {
            'raw_value': SPREAD_STEPS_PER_OCTAVE,
            'value': 12
        }
        self._dirty: bool = False
        self.arrow: int = self.__draw_arrow()
        self.pack(side="bottom")
        store.subscribe(self.__handle_store_update)

    def __handle_store_update(self) -> None:
        self._dirty = True

    def check_state(self) -> None:
        if not self._dirty:
            return
        self._dirty = False
        spread = get_music_engine_state()['spread']
        if self.state['raw_value'] != spread:
            self.__set_value(spread)

    def __draw_arrow(self) -> int:
        key_width = self.width / self.num_keys
        center = self.width / 2
        x1 = center - ((self.state['value']/2)*key_width)
        x2 = center + ((self.state['value']/2)*key_width)
        y = self.height / 2
        return self.create_line(x1, y, x2, y, fill=self.color, arrow=tk.BOTH)

    def __set_value(self, spread: float) -> None:
        self.state['raw_value'] = spread
        self.state['value'] = (spread * (12/SPREAD_STEPS_PER_OCTAVE))
        key_width = self.width / self.num_keys
        center = self.width / 2
        x1 = center - ((self.state['value']/2)*key_width)
        x2 = center + ((self.state['value']/2)*key_width)
        y = self.height / 2
        self.coords(self.arrow, x1, y, x2, y)
