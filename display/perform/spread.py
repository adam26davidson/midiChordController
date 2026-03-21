import tkinter as tk

from constants import SPREAD_STEPS_PER_OCTAVE
from redux import store


class Spread(tk.Canvas):
    width = 720
    height = 30
    num_keys = 61
    color = "#828282"

    def __init__(self, master=None):
        super().__init__(master, width=self.width, height=self.height,
                         highlightthickness=0, relief="flat", bg="#000000")
        self.state = {
            'raw_value': SPREAD_STEPS_PER_OCTAVE,
            'value': 12
        }
        self.arrow = self.__draw_arrow()
        self.pack(side="bottom")
        store.subscribe(self.handle_store_update)

    def handle_store_update(self):
        spread = store.get_state()['musicEngine']['spread']
        if self.state['raw_value'] != spread:
            self.after(0, lambda: self.__set_value(spread))

    def __draw_arrow(self):
        key_width = self.width / self.num_keys
        center = self.width / 2
        x1 = center - ((self.state['value']/2)*key_width)
        x2 = center + ((self.state['value']/2)*key_width)
        y = self.height / 2
        return self.create_line(x1, y, x2, y, fill=self.color, arrow=tk.BOTH)

    def __set_value(self, spread):
        self.state['raw_value'] = spread
        self.state['value'] = (spread * (12/SPREAD_STEPS_PER_OCTAVE))
        key_width = self.width / self.num_keys
        center = self.width / 2
        x1 = center - ((self.state['value']/2)*key_width)
        x2 = center + ((self.state['value']/2)*key_width)
        y = self.height / 2
        self.coords(self.arrow, x1, y, x2, y)
