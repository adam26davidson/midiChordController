import tkinter as tk
from constants import *
from pillow import ImageTk, Image 

class TextDisplay(tk.Frame):
  width = 270
  height = 350

  bgColor = "#000000"
  color = "#ffffff"
  inactiveColor = "#999999"
  activeColor = "#00d5ff"

  def __init__(self, master=None):
    super().__init__(master, width=self.width, height=self.height, highlightthickness=0, relief="flat", bg=self.bgColor)
    self.master = master

    bigFont = ("sans serif", 18)
    mediumFont = ("sans serif", 14)
    smallFont = ("sans serif", 12)

    # setting dsiplay
    self.settingFrame = tk.Frame(self, bg=self.bgColor, width=self.width)
    self.settingFrame.pack(side="top")
    tk.Label(self.settingFrame, text="Setting: ", fg=self.inactiveColor, bg=self.bgColor, font=smallFont).pack(side="left")
    self.setting = tk.Label(self.settingFrame, text="Loading...", bg=self.bgColor, fg=self.color, font=bigFont)
    self.setting.pack(side="left")

    # controller dsiplay
    controllerIcon = ImageTk.PhotoImage(Image.open(PARENT_PATH+"/images/controller.png"))
    self.controllerFrame = tk.Frame(self, bg=self.bgColor)
    self.controllerFrame.pack(side="top")
    tk.Label(self.controllerFrame, image=controllerIcon, bg=self.bgColor).pack(side="left")
    self.controller = tk.Label(self.controllerFrame, text="Not Connected", bg=self.bgColor, fg=self.color, font=mediumFont)
    self.controller.pack(side="left")

    # alt and shift
    self.functionFrame = tk.Frame(self, bg=self.bgColor)
    self.functionFrame.pack(side="top", pady=(10, 0))
    self.alt = tk.Label(self.functionFrame, text="alt", bg=self.bgColor, fg=self.inactiveColor, 
      font=mediumFont, highlightbackground=self.inactiveColor, highlightthickness=2, padx=5)
    self.alt.pack(side="left")
    self.shift = tk.Label(self.functionFrame, text="shift", bg=self.bgColor, fg=self.inactiveColor, 
      font=mediumFont, highlightbackground=self.inactiveColor, highlightthickness=2, padx=5)
    self.shift.pack(side="left", padx=(20, 0))

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

