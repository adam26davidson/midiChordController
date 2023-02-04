from redux import store
from ..displayConstants import COLORS
import tkinter as tk

class MenuItem(tk.Canvas):

    radius = 80
    border = 5

    inactiveColor = COLORS['chord']
    activeColor = COLORS['root']


    def __init__(self, container, text):
        super().__init__(
            container, 
            highlightthickness=0, 
            relief="flat",
            bg="#000000")
        
        self.create_oval(
            self.border/2, 
            self.border/2, 
            self.radius*2, 
            self.radius*2,
            fill="#000000", 
            outline=self.inactiveColor, 
            width=self.border)

