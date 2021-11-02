import tkinter as tk
from constants import *

class TextDisplay(tk.Frame):
  width = 100
  height = 200

  bgColor = "#000000"
  controllerColor = "#fffff"

  settingText = "Loading..."
  controllerText = "No Controller Connected"

  def __init__(self, master=None):
    super().__init__(master, width=self.width, height=self.height, highlightthickness=0, relief="flat", bg="#ffffff")
    self.master = master
    self.pack(side="top", padx=(20,20), pady=(20,20))
    self.setting = tk.Label(self, textvariable=self.settingText, width=100, height=40, bg=self.bgColor, fg="#ffffff", justify="left")
    self.setting.pack(pady=(0, 10))
    self.controller = tk.Label(self, textvariable=self.controllerText, width=100, height=40, bg=self.bgColor, fg="#ffffff", justify="left")
    self.controller.pack(pady=(0, 10))

    


