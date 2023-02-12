from ..components.numberPicker import NumberPicker
from ..components.buttonGroup import ButtonGroup
from ..components.settingsPage import SettingsPage
from ..components.slider import Slider
from ..components.settingsContainer import SettingsContainer
from constants import MAX_INVERSION_RANGE, MAX_BASS_RANGE
from redux import store
from redux.actions import musicEngine as meActions
from pyrsistent import thaw
from redux import store
from redux.actions import display as actions
import tkinter as tk

class ChordSettingsFrame(SettingsPage):

    def __init__(self, container):
        super().__init__(
            container, 'CHORD SETTINGS')

        self.topFrame = SettingsContainer(self)

        self.transposeIncrement = NumberPicker(self.topFrame, 
            name='transpose increment', 
            min=1, 
            max=11, 
            callback=self.setTransposeIncrement)

        self.inversionRange = NumberPicker(self.topFrame, 
            name='inversion range', 
            min=1, 
            max=MAX_INVERSION_RANGE, 
            callback=self.setInversionRange)

        self.bassRange = NumberPicker(self.topFrame, 
            name='bass range', 
            min=1, 
            max=MAX_BASS_RANGE, 
            callback=self.setBassRange)

        self.transposeIncrement.pack(side='left', anchor="nw", pady=(5, 5), padx=(5, 5))
        self.inversionRange.pack(side='left', anchor="nw", pady=(5, 5), padx=(5, 5))
        self.bassRange.pack(side='left', anchor="nw", pady=(5, 5), padx=(5, 5))
        
        self.topFrame.grid(row=1, column=0, sticky='new', padx=(5, 5))
        

    def setTransposeIncrement(self, increment):
        store.dispatch(meActions.changeTransposeIncrement(increment))
    
    def setInversionRange(self, range):
        store.dispatch(meActions.changeInversionRange(range))

    def setBassRange(self, range):
        store.dispatch(meActions.changeBassRange(range))
