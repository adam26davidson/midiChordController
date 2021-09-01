import tkinter as tk
from constants import *

class Inversion(tk.Canvas):
  width = 50
  height = 380

  bgColor = "#262626"
  separatorColor = "#9c9c9c"
  thumbColor = "#ffffff"

  def __init__(self, master=None):
    super().__init__(master, width=self.width, height=self.height, highlightthickness=0, relief="flat", bg=self.bgColor)
    self.master = master
    self.separators = []
    self.activeShader = None
    self.thumb = self.create_line(0, self.height/2, self.width, self.height/2, fill = self.thumbColor)
    self.max = 3
    self.activeRegion = 0
    self.pack(side="right", padx=20)

  def setMax(self, max, activeRegion):
    self.max = max
    self.activeRegion = activeRegion
    self.setActiveRegion(activeRegion)

  def setActiveRegion(self, region):
    self.activeRegion = region
    if self.activeShader:
      self.delete(self.activeShader)
    slotHeight = self.height / (2 * (self.max + 1))
    snap = slotHeight * INVERSION_SNAP
    yt, yb = 0, 0
    if region >= self.max:
      yt = 0
      yb = slotHeight + snap
    elif region <= (-1*self.max):
      yt = (self.height - slotHeight) - snap
      yb = self.height
    elif region == 0:
      yt = (self.height / 2) - (slotHeight + snap)
      yb = (self.height / 2) + (slotHeight + snap)
    elif region > 0:
      yt = (slotHeight * (self.max - region)) - snap
      yb = (slotHeight * ((self.max+1) - region)) + snap
    elif region < 0:
      yt = ((self.height / 2) + ((-1*region)*slotHeight)) - snap
      yb = ((self.height / 2) + (((-1*region)+1)*slotHeight)) + snap
    self.activeShader = self.create_rectangle(0, yt, self.width, yb, fill="#6b6b6b")
    self.drawSeparators()

  def positionThumb(self, value):
    y = (self.height/2) - value*(self.height/2)
    self.thumb.coords(0, y, self.width, y)

  def drawSeparators(self):
    slotHeight = self.height / (2 * (self.max + 1))
    snap = slotHeight * INVERSION_SNAP
    for separator in self.separators:
      self.delete(separator)
    separators = []
    for i in range(-1*self.max, 0):
      snapOffset = 0
      if i == self.activeRegion - 1:
        snapOffset = snap
      elif i == self.activeRegion:
        snapOffset = -1*snap
      y = slotHeight * (-1*i) + (self.height / 2.0) + snapOffset
      separators.append(self.create_line(0, y, self.width, y, fill=self.separatorColor))

    for i in range(1, self.max + 1):
      snapOffset = 0
      if i == self.activeRegion + 1:
        snapOffset = -1*snap
      elif i == self.activeRegion:
        snapOffset = snap
      y = (slotHeight * ((self.max+1) -i)) + snapOffset
      separators.append(self.create_line(0, y, self.width, y, fill=self.separatorColor))

    self.separators = separators