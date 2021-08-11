import tkinter as tk
import ui.keyboard as keyboard

class Display(tk.Frame):
  def __init__(self, master=None):
    self.height = 480
    self.width = 800
    super().__init__(master=master, height=self.height, width=self.width, bg="#000")
    self.master = master
    self.keyboard = keyboard.Keyboard(master=self)
    self.pack(side="bottom")


window = tk.Tk()
window.geometry("800x480")
display = Display(master=window)
display.keyboard.playNotes([67, 70])
window.mainloop()