import tkinter as tk
from constants import *

class TextDisplay(tk.Frame):
  width = 250
  height = 350

  bgColor = "#000000"
  controllerColor = "#fffff"

  def __init__(self, master=None):
    super().__init__(master, width=self.width, height=self.height, highlightthickness=0, relief="flat", bg="#ffffff")
    self.master = master

    self.setting = tk.Label(self, text="Loading...", bg=self.bgColor, fg="#ffffff", justify="left")
    self.setting.pack()
    self.controller = tk.Label(self, text="No Controller Connected", bg=self.bgColor, fg="#ffffff", justify="left")
    self.controller.pack()

    self.pack(side="top", padx=(20,20), pady=(20,20))

  def setSetting(self, name):
    self.setting.configure(text=name)

  def setController(self, name):
    self.controller.configure(text=name)
