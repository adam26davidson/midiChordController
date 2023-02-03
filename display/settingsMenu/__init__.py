from redux import store
from pyrsistent import thaw
import tkinter as tk

class SettingsMenuFrame(tk.Frame):

    height = 480
    width = 800

    def __init__(self, container):
        super().__init__(container, width=self.width, height=self.height, highlightthickness=0, relief="flat", bg="#000000")

        
        self.pack()