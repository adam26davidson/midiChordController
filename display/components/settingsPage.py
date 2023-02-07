from ..displayConstants import FONTS, COLORS
from redux import store
from redux.actions import musicEngine as meActions
from pyrsistent import thaw
from redux import store
from redux.actions import display as actions
import tkinter as tk

class SettingsPage(tk.Frame):

    def __init__(self, container, name):
        super().__init__(
            container, 
            highlightthickness=0, 
            relief="flat", 
            bg="#000000")

        self.titleFrame = tk.Frame(self, 
            highlightthickness=0, 
            relief="flat", 
            bg="#000000",
            height=100)
        
        self.title = tk.Label(self.titleFrame,
            text=name,
            bg='#000000', 
            fg=COLORS['chord'], 
            font=FONTS["big"],
            justify='center')
        
        self.menuButton = tk.Button(self.titleFrame,
            highlightthickness=0, 
            relief="flat",
            bg="#000000",
            height=2,
            width=7,
            bd=0,
            activebackground="#000000",
            fg=COLORS['chord'],
            activeforeground=COLORS['root'],
            font=FONTS["big"],
            disabledforeground=COLORS['chordDim'],
            text='\u25C0 MENU',
            command=lambda: store.dispatch(actions.changeActiveFrame('MENU')))

        self.menuButton.place(rely=0.5, relx=0.25, anchor='center')
        self.title.place(rely=0.5, relx=0.5, anchor='center')
        self.titleFrame.grid(row=0, column=0, sticky='new')


        self.grid(row=0, column=0, sticky='nsew')

