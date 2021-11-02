import tkinter as tk
from constants import *

class TextDisplay(tk.Frame):
  width = 200
  height = 200

  bgColor = "#000000"
  controllerColor = "#fffff"

  settingText = "Loading..."
  controllerText = "No Controller Connected"

  def __init__(self, master=None):
    super().__init__(master, width=self.width, height=self.height, highlightthickness=0, relief="flat", bg=self.bgColor)
    self.master = master
    self.setting = tk.Label(self, textvariable=self.settingText, width=200, height=20, bg=self.bgColor, fg="#ffffff")
    self.setting.pack(side="left", pady=(0, 10))
    self.controller = tk.Label(self, textvariable=self.controllerText, width=200, height=20, bg=self.bgColor, fg="#ffffff")
    self.controller.pack(side="left", pady=(0, 10))

    self.pack(side="top", padx=(20,20), pady=(20,20))


