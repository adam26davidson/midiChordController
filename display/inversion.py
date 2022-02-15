import tkinter as tk
from constants import *
from .displayConstants import COLORS

class Inversion(tk.Canvas):
  width = 40
  height = 370

  bgColor = "#000000"
  separatorColor = COLORS['chordDim']
  shaderColor = "#2e2e2e"
  thumbColor = COLORS['root']

  def __init__(self, master=None):
    super().__init__(master, width=self.width, height=self.height, highlightthickness=0, relief="flat", bg=self.bgColor)
    self.master = master
    self.separators = []
    self.activeShader = None
    self.thumb = self.create_line(0, self.height/2, self.width, self.height/2, fill = self.thumbColor, width=3)
    self.max = 3
    self.activeRegion = 0
    self.pack(side="right", padx=(0,20), pady=(20,0))

  def setMax(self, max, activeRegion):
    self.max = max
    self.activeRegion = activeRegion
    self.setActiveRegion(activeRegion)

  def setActiveRegion(self, region):
    self.activeRegion = region
    if self.activeShader:
      self.delete(self.activeShader)
    slotHeight = self.height / ((2 * self.max) + 1)
    snap = slotHeight * INVERSION_SNAP
    yt, yb = 0, 0
    if region >= self.max:
      yt = 0
      yb = slotHeight + snap
    elif region <= (-1*self.max):
      yt = (self.height - slotHeight) - snap
      yb = self.height
    else:
      yt = (slotHeight*(-1*region + self.max)) - snap
      yb = (slotHeight*(-1*region + self.max + 1)) + snap 
    #self.activeShader = self.create_rectangle(-1, yt, self.width, yb, fill=self.shaderColor)
    self.drawSeparators()

  def positionThumb(self, value):
    y = (self.height/2) - value*(self.height/2)
    self.coords(self.thumb, 0, y, self.width, y)
    self.tag_raise(self.thumb)

  def drawSeparators(self):
    slotHeight = self.height / ((2 * self.max) + 1)
    snap = slotHeight * INVERSION_SNAP
    for separator in self.separators:
      self.delete(separator)
    separators = []
    for i in range(-1*self.max, self.max):
      snapOffset = 0
      if i == (self.activeRegion * -1) - 1:
        snapOffset = -snap
      elif i == (self.activeRegion * -1):
        snapOffset = snap
      y = slotHeight * (i + self.max + 1) + snapOffset
      separators.append(self.create_line(0, y, self.width, y, fill=self.separatorColor width= 2))

    self.separators = separators