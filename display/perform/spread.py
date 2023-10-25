import tkinter as tk
from constants import SPREAD_STEPS_PER_OCTAVE
from redux import store


class Spread(tk.Canvas):
    width = 720
    height = 30
    numKeys = 61
    color = "#828282"

    def __init__(self, master=None):
        super().__init__(master, width=self.width, height=self.height,
                         highlightthickness=0, relief="flat", bg="#000000")
        self.state = {
            'rawValue': SPREAD_STEPS_PER_OCTAVE,
            'value': 12
        }
        self.arrow = self.__drawArrow()
        self.pack(side="bottom")
        store.subscribe(self.handleStoreUpdate)

    def handleStoreUpdate(self):
        spread = store.get_state()['musicEngine']['spread']
        if self.state['rawValue'] != spread:
            self.__setValue(spread)

    def __drawArrow(self):
        keyWidth = self.width / self.numKeys
        center = self.width / 2
        x1 = center - ((self.state['value']/2)*keyWidth)
        x2 = center + ((self.state['value']/2)*keyWidth)
        y = self.height / 2
        return self.create_line(x1, y, x2, y, fill=self.color, arrow=tk.BOTH)

    def __setValue(self, spread):
        self.state['rawValue'] = spread
        self.state['value'] = (spread * (12/SPREAD_STEPS_PER_OCTAVE))
        keyWidth = self.width / self.numKeys
        center = self.width / 2
        x1 = center - ((self.state['value']/2)*keyWidth)
        x2 = center + ((self.state['value']/2)*keyWidth)
        y = self.height / 2
        self.coords(self.arrow, x1, y, x2, y)
