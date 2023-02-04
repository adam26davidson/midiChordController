from redux import store
from ..displayConstants import COLORS
import tkinter as tk

class MenuItem(tk.Canvas):

    radius = 50
    border = 3

    inactiveColor = COLORS['chord']
    activeColor = COLORS['root']


    def __init__(self, container, text):
        super().__init__(
            container, 
            highlightthickness=0, 
            relief="flat", 
            bg="#000000")
        
        self.create_oval(0, 0, self.radius, self.radius,
            fill="#000000", 
            outline=self.inactiveColor, 
            width=self.border)

