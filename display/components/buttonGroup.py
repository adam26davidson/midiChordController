from redux import store
from ..displayConstants import FONTS, COLORS
from .settingControl import SettingControl
from pyrsistent import thaw
from redux import store
from redux.actions import display as actions
import tkinter as tk

class ButtonGroup(SettingControl):

    def __init__(self, container, name, optionsList, selected, callback):
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
            self.buttons[option['name']] = SingleButton(self.contentsFrame, option, self.setSelectedButton)
            self.buttons[option['name']].pack(side='left')
        
        self.buttons[selected].setSelected()

        self.contentsFrame.pack(side='top', anchor='nw', padx=(4, 4), pady=(4, 4))
    
    def setSelectedButton(self, value, name):
        self.buttons[self.state.activebutton].setUnSelected()
        self.buttons[name].setSelected()
        self.state.activebutton = name
        self.callback(value) 
    
    def setDisabled(self):
        for buttonName in self.buttons.keys():
            button = self.buttons[buttonName]
            button.configure(state=tk.DISABLED)
            if buttonName == self.state.activebutton:
                button.configure(
                    bg=COLORS['chordDim'],
                    fg='#000000'
                )
    
    def setEnabled(self):
        for buttonName in self.buttons.keys():
            button = self.buttons[buttonName]
            button.configure(state=tk.NORMAL)
            if buttonName == self.state.activebutton:
                button.configure(
                    bg=COLORS['root'],
                    fg='#000000'
                )
                

class SingleButton(tk.Button):

    def __init__(self, container, option, callback):
        self.value = option['value']
        self.name = option['name']
        self.callback = callback
        super().__init__(container,
            highlightthickness=0, 
            relief="flat",
            height=3,
            width=5,
            bd=4,
            bg="#000000",
            activebackground="#000000",
            fg=COLORS['chordDim'],
            activeforeground=COLORS['chord'],
            font=FONTS["medium"],
            disabledforeground=COLORS['chordDim'],
            text=option['name'],
            command=self.__onClick)
        
    def __onClick(self):
        self.callback(self.value, self.name)
    
    def setSelected(self):
        self.configure(
            bg=COLORS['root'],
            activebackground=COLORS['root'],
            fg="#000000",
            activeforeground="#000000")
    
    def setUnSelected(self):
        self.configure(
            bg="#000000",
            activebackground="#000000",
            fg=COLORS['chordDim'],
            activeforeground=COLORS['chordDim'])


class ButtonGroupState():
    disabled = False
    activebutton = ''

    def __init__(self, activeButton):
        self.activebutton = activeButton
