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
    self.controller = tk.Label(self, textvariable=self.controllerText)
    self.controller.pack(side="top", pady=(0, 10))
    self.pack(side="top", padx=(20,20), pady=(20,20))


