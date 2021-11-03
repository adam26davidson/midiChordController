import tkinter as tk
from constants import *

class TextDisplay(tk.Frame):
  width = 250
  height = 350

  bgColor = "#000000"
  color = "#ffffff"
  activeColor = "#0366fc"

  def __init__(self, master=None):
    super().__init__(master, width=self.width, height=self.height, highlightthickness=0, relief="flat", bg=self.bgColor)
    self.master = master

    bigFont = ("sans serif", 18)
    mediumFont = ("sans serif", 14)
    smallFont = ("sans serif", 12)

    self.settingFrame = tk.Frame(self, bg=self.bgColor)
    self.settingFrame.pack(side="top")
    tk.Label(self.settingFrame, text="setting: ", fg=self.color, bg=self.bgColor, font=smallFont).pack(side="left")
    self.setting = tk.Label(self.settingFrame, text="Loading...", bg=self.bgColor, fg=self.color, font=bigFont)
    self.setting.pack(side="left")

    self.controllerFrame = tk.Frame(self, bg=self.bgColor)
    self.controllerFrame.pack(side="top")
    tk.Label(self.controllerFrame, text="controller: ", fg=self.color, bg=self.bgColor, font=smallFont).pack(side="left")
    self.controller = tk.Label(self.controllerFrame, text="Not Connected", bg=self.bgColor, fg=self.color, font=mediumFont)
    self.controller.pack(side="left")

    self.functionFrame = tk.Frame(self, bg=self.bgColor)
    self.functionFrame.pack(side="top", pady=(10, 0))
    self.alt = tk.Label(self.functionFrame, text="alt", bg=self.bgColor, fg=self.color, font=mediumFont, highlightbackground=self.color)
    self.alt.pack(side="left")
    self.shift = tk.Label(self.functionFrame, text="shift", bg=self.bgColor, fg=self.color, font=mediumFont, highlightbackground=self.color)
    self.shift.pack(side="left", padx=(10, 0))

    self.pack(side="top", padx=(20,20), pady=(20,20))

  def setSetting(self, name):
    self.setting.configure(text=name)

  def setController(self, name):
    self.controller.configure(text=name)
  
  def setAlt(self, active):
    if active:
      self.alt.configure(fg=self.activeColor)
    else:
      self.alt.configure(fg=self.color)

  def setShift(self, active):
    if active:
      self.shift.configure(fg=self.activeColor)
    else:
      self.shift.configure(fg=self.color)

