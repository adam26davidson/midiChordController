import tkinter as tk

class SettingsContainer(tk.Frame):

    def __init__(self, container):
        super().__init__(
            container, 
            highlightthickness=0, 
            relief="flat", 
            bg="#000000")
