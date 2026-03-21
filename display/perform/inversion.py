import tkinter as tk

from constants import INVERSION_SNAP

from ..display_constants import COLORS


class Inversion(tk.Canvas):
    width = 20
    height = 370

    thumb_radius = 3

    bg_color = "#000000"
    separator_color = COLORS['chordDim']
    shader_color = "#2e2e2e"
    thumb_color = COLORS['root']

    def __init__(self, master=None):
        super().__init__(master, width=self.width, height=self.height,
                         highlightthickness=0, relief="flat", bg=self.bg_color)
        self.parent = master
        self.separators = []
        self.active_shader = None
        self.thumb = self.create_line(
            0, self.height/2, self.width, self.height/2,
            fill=self.thumb_color, width=3)
        self.max = 3
        self.active_region = 0
        self.draw_separators()
        self.pack(side="right", padx=(0, 40), pady=(20, 0))

    def set_max(self, max, active_region):
        self.max = max
        self.active_region = active_region
        self.set_active_region(active_region, 'continuous')

    def set_active_region(self, region, mode):
        self.active_region = region
        if self.active_shader:
            self.delete(self.active_shader)
        self.draw_separators()
        if mode == 'incremental':
            value = (2*region) / (2*self.max + 1)
            self.position_thumb(value)

    def position_thumb(self, value):
        y = (self.height/2) - value*(self.height/2)
        self.coords(self.thumb, 0, y, self.width, y)
        self.tag_raise(self.thumb)

    def draw_separators(self):
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
