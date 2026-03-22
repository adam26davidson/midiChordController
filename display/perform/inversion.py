from __future__ import annotations

import tkinter as tk

from constants import INVERSION_SNAP

from ..display_constants import COLORS


class Inversion(tk.Canvas):
    width: int = 20
    height: int = 370

    thumb_radius: int = 3

    bg_color: str = "#000000"
    separator_color: str = COLORS['chordDim']
    shader_color: str = "#2e2e2e"
    thumb_color: str = COLORS['root']

    def __init__(self, master: tk.Misc | None = None) -> None:
        super().__init__(master, width=self.width, height=self.height,
                         highlightthickness=0, relief="flat", bg=self.bg_color)
        self.parent = master
        self.separators: list[int] = []
        self.active_shader: int | None = None
        self.thumb: int = self.create_line(
            0, self.height/2, self.width, self.height/2,
            fill=self.thumb_color, width=3)
        self.max: int = 3
        self.active_region: int = 0
        self.draw_separators()
        self.pack(side="right", padx=(0, 40), pady=(20, 0))

    def set_max(self, max: int, active_region: int) -> None:
        self.max = max
        self.active_region = active_region
        self.set_active_region(active_region, 'continuous')

    def set_active_region(self, region: int, mode: str) -> None:
        self.active_region = region
        if self.active_shader:
            self.delete(self.active_shader)
        self.draw_separators()
        if mode == 'incremental':
            value = (2*region) / (2*self.max + 1)
            self.position_thumb(value)

    def position_thumb(self, value: float) -> None:
        y = (self.height/2) - value*(self.height/2)
        self.coords(self.thumb, 0, y, self.width, y)
        self.tag_raise(self.thumb)

    def draw_separators(self) -> None:
        num_separators = 2 * self.max
        slot_height = self.height / ((2 * self.max) + 1)
        snap = slot_height * INVERSION_SNAP

        # Recreate lines only if count changed
        if len(self.separators) != num_separators:
            for separator in self.separators:
                self.delete(separator)
            self.separators = [
                self.create_line(0, 0, self.width, 0, fill=self.separator_color, width=2)
                for _ in range(num_separators)
            ]

        # Reposition existing lines
        for idx, i in enumerate(range(-1*self.max, self.max)):
            snap_offset = 0
            if i == (self.active_region * -1) - 1:
                snap_offset = -snap
            elif i == (self.active_region * -1):
                snap_offset = snap
            y = slot_height * (i + self.max + 1) + snap_offset
            self.coords(self.separators[idx], 0, y, self.width, y)
