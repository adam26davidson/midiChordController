from redux import store
from pyrsistent import thaw
import tkinter as tk
from .menuItem import MenuItem

class SettingsMenuFrame(tk.Frame):

    height = 480
    width = 800

    def __init__(self, container):
        super().__init__(
            container, 
            highlightthickness=0, 
            relief="flat", 
            bg="#ffffff")

        self.grid(row=0, column=0, sticky='nsew')

        self.performItem = MenuItem(self, "PERFORM")
        self.performItem.place(anchor='center')
