import tkinter as tk
from constants import *

class Spread(tk.Canvas):
  width = 726
  height = 20
  color = "#ffffff"
  
  def __init__(self, master=None):
    super().__init__(master, width=self.width, height=self.height, highlightthickness=0, relief="flat", bg="#000000")
    self.value = 12
    self.arrow = self.drawArrow()

  def drawArrow(self):
    keyWidth = self.width / 88
    center = keyWidth * (CENTER_NOTE - 21)
    x1 = center - ((self.value/2)*keyWidth)
    x2 = center + ((self.value/2)*keyWidth)
    y = self.height / 2
    return self.create_line(x1, y, x2, y, fill=self.color, arrow=tk.BOTH)

  def setValue(self, spread):
    self.value = (spread * (12/SPREAD_STEPS_PER_OCTAVE)) + 12
    keyWidth = self.width / 88
    center = keyWidth * (CENTER_NOTE - 21)
    x1 = center - ((self.value/2)*keyWidth)
    x2 = center + ((self.value/2)*keyWidth)
    y = self.height / 2
    self.coords(self.arrow, x1, y, x2, y)