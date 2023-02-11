from ..components.numberPicker import NumberPicker
from ..components.buttonGroup import ButtonGroup
from ..components.settingsPage import SettingsPage
from ..components.slider import Slider
from ..components.settingsContainer import SettingsContainer
from redux import store
from redux.actions import musicEngine as meActions
from pyrsistent import thaw
from redux import store
from redux.actions import display as actions
import tkinter as tk

class StrumSettingsFrame(SettingsPage):

    def __init__(self, container):
        super().__init__(
            container, 'STRUM SETTINGS')

        self.topFrame = SettingsContainer(self)
        self.bottomFrame = SettingsContainer(self)

        self.strumMode = ButtonGroup(self.topFrame, 
            name='strum mode',
            optionsList=[
                {'name': 'RAND', 'value': 'random'}, 
                {'name': 'REG', 'value': 'regular'},
                {'name': 'OFF', 'value': 'off'},
            ],
            selected='REG',
            callback=self.setStrumMode)
        
        self.strumOrder = ButtonGroup(self.topFrame, 
            name='strum order',
            optionsList=[
                {'name': 'UP', 'value': 'up'}, 
                {'name': 'DOWN', 'value': 'down'},
                {'name': 'RAND', 'value': 'random'},
            ],
            selected='RAND',
            callback=self.setStrumOrder)
        
        self.strumInterval = Slider(self.bottomFrame, 
            name='strum interval',
            min=0,
            max=1,
            resolution=0.005,
            digits=4,
            value=0.02,
            callback=self.setStrumInterval)

        self.strumMode.pack(side='left', anchor="nw", pady=(5, 5), padx=(5, 5))
        self.strumOrder.pack(side='left', anchor="nw", pady=(5, 5), padx=(5, 5))
        self.topFrame.grid(row=1, column=0, sticky='new', padx=(5, 5))

        self.strumInterval.pack(side='left', anchor="nw", pady=(5, 5), padx=(5, 5))
        self.bottomFrame.grid(row=2, column=0, sticky='new', padx=(5, 5))
        

    def setStrumMode(self, mode):
        store.dispatch(meActions.changeStrumMode(mode))
        if mode == 'off':
            self.strumInterval.setDisabled()
            self.strumOrder.setDisabled()
        else:
            self.strumInterval.setEnabled()
            self.strumOrder.setEnabled()
    
    def setStrumInterval(self, interval):
        store.dispatch(meActions.changeStrumInterval(interval))

    def setStrumOrder(self, order):
        store.dispatch(meActions.changeStrumOrder(order))
