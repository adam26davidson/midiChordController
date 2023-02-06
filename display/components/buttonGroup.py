from redux import store
from ..displayConstants import FONTS, COLORS
from .settingControl import SettingControl
from pyrsistent import thaw
from redux import store
from redux.actions import display as actions
import tkinter as tk

class ButtonGroup(SettingControl):

    def __init__(self, container, name, optionsList, callback):
        super().__init__(container, name)

        self.optionsList = optionsList
        self.callback = callback

        self.state = ButtonGroupState(optionsList[0]['name'])

        self.contentsFrame = tk.Frame(self, 
            highlightthickness=0, 
            relief="flat", 
            bg="#000000")
        
        self.buttons = {}

        for option in optionsList:
            self.buttons[option['name']] = SingleButton(self, self.contentsFrame, option, self.setSelectedButton)
        
        self.contentsFrame.pack(side='top', anchor='nw', padx=(2, 2), pady=(2, 2))
    
    def setSelectedButton(self, value, name):
        self.buttons[self.state.activebutton].setUnSelected()
        self.buttons[name].setSelected()
        self.state.activebutton = name
        self.callback(value) 

class SingleButton(tk.Button):

    def __init__(self, container, option, callback):
        self.value = option['value']
        self.name = option['name']
        self.callback
        super().__init__(container,
            highlightthickness=0, 
            relief="flat",
            height=2,
            width=4,
            bd=4,
            bg="#000000",
            activebackground="#000000",
            fg=COLORS['chord'],
            activeforeground=COLORS['chord'],
            font=FONTS["medium"],
            disabledforeground=COLORS['chordDim'],
            text=option['name'],
            command=self.__onClick)
        
    def __onClick(self):
        self.callback(self.value, self.name)
    
    def setSelected(self):
        self.configure(
            bg=COLORS['chord'],
            activebackground=COLORS['chord'],
            fg="#000000",
            activeforeground="#000000")
    
    def setUnSelected(self):
        self.configure(
            bg="#000000",
            activebackground="#000000",
            fg=COLORS['chord'],
            activeforeground=COLORS['chord'])


class ButtonGroupState():
    disabled = False
    activebutton = ''

    def __init__(self, activeButton):
        self.activebutton = activeButton
