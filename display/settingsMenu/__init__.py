from redux import store
from pyrsistent import thaw
import tkinter as tk

class SettingsMenuFrame(tk.Frame):

    height = 480
    width = 800

    def __init__(self, container, controller):
        super().__init__(
            container=container, 
            width=self.width, 
            height=self.height, 
            highlightthickness=0, 
            relief="flat", 
            bg="#000000"
        )
        self.performButton = tk.Button(self, height=20, width=20, text='TEST', bg='#ffffff')
        self.performButton.pack()
        self.controller = controller
        self.pack()