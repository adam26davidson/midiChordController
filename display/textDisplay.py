import tkinter as tk
from constants import *

class TextDisplay(tk.Frame):
  width = 250
  height = 350

  bgColor = "#000000"
  controllerColor = "#fffff"

  def __init__(self, master=None):
    super().__init__(master, width=self.width, height=self.height, highlightthickness=0, relief="flat", bg=self.bgColor)
    self.master = master
    settingFont = ("sans serif", 18)
    controllerFont = ("sans serif", 14)

    self.settingFrame = tk.Frame(self, bg=self.bgColor)
    self.settingFrame.pack(side="top")
    tk.Label(self.settingFrame, text="setting: ", fg="#ffffff", bg=self.bgColor).pack(side="left")
    self.setting = tk.Label(self.settingFrame, text="Loading...", bg=self.bgColor, width=self.width, fg="#ffffff", justify="left", font=settingFont)
    self.setting.pack(side="left")

    self.controllerFrame = tk.Frame(self, bg=self.bgColor)
    self.controllerFrame.pack(side="top")
    tk.Label(self.controllerFrame, text="controller: ", fg="#ffffff", bg=self.bgColor).pack(side="left")
    self.controller = tk.Label(self.controllerFrame, text="Not Connected", bg=self.bgColor, width=self.width, fg="#ffffff", justify="left", font=controllerFont)
    self.controller.pack(side="left")

    self.pack(side="top", padx=(20,20), pady=(20,20))

  def setSetting(self, name):
    self.setting.configure(text=name)

  def setController(self, name):
    self.controller.configure(text=name)
