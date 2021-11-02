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
    settingFont = ("sans serif", 20)
    controllerFont = ("sans serif", 15)

    tk.Label(self, text="setting: ", fg="#ffffff", bg=self.bgColor).pack(side="left")
    self.setting = tk.Label(self, text="Loading...", bg=self.bgColor, width=self.width, fg="#ffffff", justify="left", font=settingFont)
    self.setting.pack(side="left", pady=(0, 10))
    
    tk.Label(self, text="controller: ", fg="#ffffff", bg=self.bgColor).pack(side="left")
    self.controller = tk.Label(self, text="Not Connected", bg=self.bgColor, width=self.width, fg="#ffffff", justify="left", font=controllerFont)
    self.controller.pack(side="left", pady=(0, 10))

    self.pack(side="top", padx=(20,20), pady=(20,20))

  def setSetting(self, name):
    self.setting.configure(text=name)

  def setController(self, name):
    self.controller.configure(text=name)
