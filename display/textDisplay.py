import tkinter as tk
from constants import *
from .displayConstants import FONTS, COLORS
from PIL import ImageTk, Image 
from redux import store

class TextDisplay(tk.Frame):
  width = 270
  height = 350

  bgColor = "#000000"
  color = COLORS["chord"]
  inactiveColor = COLORS["chordDim"]
  activeColor = COLORS["root"]

  def __init__(self, master=None):
    super().__init__(master, width=self.width, height=self.height, highlightthickness=0, relief="flat", bg=self.bgColor)
    self.master = master

    bigFont = FONTS["big"]
    mediumFont = FONTS["medium"]
    smallFont = FONTS["small"]

    # setting dsiplay
    self.settingFrame = tk.Frame(self, bg=self.bgColor, width=self.width)
    self.settingFrame.pack(side="top")
    tk.Label(self.settingFrame, text="Setting: ", fg=self.inactiveColor, bg=self.bgColor, font=smallFont).pack(side="left")
    self.setting = tk.Label(self.settingFrame, text="Loading...", bg=self.bgColor, fg=self.color, font=bigFont)
    self.setting.pack(side="left")

    # controller dsiplay
    self.controllerImage = Image.open(PARENT_PATH+"display/images/game-controller.png")
    self.controllerIcon = ImageTk.PhotoImage(self.controllerImage)
    self.controllerFrame = tk.Frame(self, bg=self.bgColor)
    self.controllerFrame.pack(side="top")
    tk.Label(self.controllerFrame, image=self.controllerIcon, bg=self.bgColor).pack(side="left")
    self.controller = tk.Label(self.controllerFrame, text="Not Connected", bg=self.bgColor, fg=self.color, font=mediumFont)
    self.controller.pack(side="left", padx=(10, 0))

    # alt and shift
    self.functionFrame = tk.Frame(self, bg=self.bgColor)
    self.functionFrame.pack(side="top", pady=(10, 0))
    self.alt = tk.Label(self.functionFrame, text="alt", bg=self.bgColor, fg=self.inactiveColor, 
      font=mediumFont, highlightbackground=self.inactiveColor, highlightthickness=2, padx=5)
    self.alt.pack(side="left")
    self.shift = tk.Label(self.functionFrame, text="shift", bg=self.bgColor, fg=self.inactiveColor, 
      font=mediumFont, highlightbackground=self.inactiveColor, highlightthickness=2, padx=5)
    self.shift.pack(side="left", padx=(40, 0))

    self.pack(side="top", padx=(20,20), pady=(20,20))

  def setSetting(self, name):
    self.setting.configure(text=name)

  def setController(self, name):
    self.controller.configure(text=name)
  
  def setAlt(self, active):
    if active:
      self.alt.configure(fg=self.activeColor, highlightbackground=self.activeColor)
    else:
      self.alt.configure(fg=self.inactiveColor, highlightbackground=self.inactiveColor)

  def setShift(self, active):
    if active:
      self.shift.configure(fg=self.activeColor, highlightbackground=self.activeColor)
    else:
      self.shift.configure(fg=self.inactiveColor, highlightbackground=self.inactiveColor)

