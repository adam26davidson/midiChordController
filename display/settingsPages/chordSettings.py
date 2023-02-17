from ..components.numberPicker import NumberPicker
from ..components.buttonGroup import ButtonGroup
from ..components.settingsPage import SettingsPage
from ..components.slider import Slider
from ..components.settingsContainer import SettingsContainer
from constants import MAX_INVERSION_RANGE, MAX_BASS_RANGE
from redux import store
from redux.actions import musicEngine as meActions
from redux.settingsStorage import SettingsStorageUtility
from pyrsistent import thaw
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
            value=1,
            callback=self.setTransposeIncrement)

        self.inversionRange = NumberPicker(self.topFrame, 
            name='inversion range', 
            min=1, 
            max=MAX_INVERSION_RANGE, 
            value=4,
            callback=self.setInversionRange)

        self.bassRange = NumberPicker(self.topFrame, 
            name='bass range', 
            min=1, 
            max=MAX_BASS_RANGE, 
            value=4,
            callback=self.setBassRange)

        self.transposeIncrement.pack(side='left', anchor="nw", pady=(5, 5), padx=(5, 5))
        self.inversionRange.pack(side='left', anchor="nw", pady=(5, 5), padx=(5, 5))
        self.bassRange.pack(side='left', anchor="nw", pady=(5, 5), padx=(5, 5))

        self.topFrame.grid(row=1, column=0, sticky='new', padx=(5, 5))
        
        store.subscribe(self.__handleStoreUpdate)

        self.settingsStorage = SettingsStorageUtility()


    def __handleStoreUpdate(self):
        state = store.get_state()
        meState = thaw(state['musicEngine'])

        if meState['transposeIncrement'] != self.transposeIncrement.getValue():
            self.transposeIncrement.setValue(meState['transposeIncrement'])
        if meState['inversionRange'] != self.inversionRange.getValue():
            self.inversionRange.setValue(meState['inversionRange'])
        if meState['bassRange'] != self.bassRange.getValue():
            self.bassRange.setValue(meState['bassRange'])

    def setTransposeIncrement(self, increment):
        store.dispatch(meActions.changeTransposeIncrement(increment))
    
    def setInversionRange(self, range):
        store.dispatch(meActions.changeInversionRange(range))

    def setBassRange(self, range):
        store.dispatch(meActions.changeBassRange(range))
