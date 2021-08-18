import tkinter as tk
from keyboard import Keyboard

class Display():
  def __init__(self, callBack):
    self.height = 480
    self.width = 800

    self.root = tk.Tk()
    self.root.geometry("800x480")

    self.keyboard = Keyboard(master=self.root)
    self.root.after(0, callBack)
    self.root.mainloop()