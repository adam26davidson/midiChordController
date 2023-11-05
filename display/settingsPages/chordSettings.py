from ..components.numberPicker import NumberPicker
from ..components.buttonGroup import ButtonGroup
from ..components.settingsPage import SettingsPage
from ..components.settingsContainer import SettingsContainer
from constants import MAX_INVERSION_RANGE, MAX_BASS_RANGE
from redux import store
from redux.actions import musicEngine as meActions
from redux.settingsStorage import settingsStorageUtility
from pyrsistent import thaw
import tkinter as tk

class ChordSettingsFrame(SettingsPage):

    def __init__(self, container):
        super().__init__(
            container, 'CHORD SETTINGS')

        self.rowOne = SettingsContainer(self)

        self.transposeIncrement = NumberPicker(self.rowOne, 
            name='transpose increment', 
            min=1, 
            max=11, 
            value=1,
            callback=self.setTransposeIncrement)

        self.inversionRange = NumberPicker(self.rowOne, 
            name='inversion range', 
            min=1, 
            max=MAX_INVERSION_RANGE, 
            value=4,
            callback=self.setInversionRange)

        self.bassRange = NumberPicker(self.rowOne, 
            name='bass range', 
            min=1, 
            max=MAX_BASS_RANGE, 
            value=4,
            callback=self.setBassRange)
        
        self.controlMode = ButtonGroup(self.channelFrame, 
            name='control mode',
            optionsList=[{'name': 'INT', 'value': 'internal'}, {'name': 'EXT', 'value': 'external'}],
            selected='NO',
            callback=self.setControlMode)

        self.transposeIncrement.pack(side='left', anchor="nw", pady=(5, 5), padx=(5, 5))
        self.inversionRange.pack(side='left', anchor="nw", pady=(5, 5), padx=(5, 5))
        self.bassRange.pack(side='left', anchor="nw", pady=(5, 5), padx=(5, 5))

        self.rowOne.grid(row=1, column=0, sticky='new', padx=(5, 5))
        
        self.rowTwo = SettingsContainer(self)

        self.controlMode = ButtonGroup(self.rowTwo, 
            name='control mode',
            optionsList=[{'name': 'INT', 'value': 'internal'}, {'name': 'EXT', 'value': 'external'}],
            selected='NO',
            callback=self.setControlMode)
        
        self.controlMode.pack(side='left', anchor="nw", pady=(5, 5), padx=(5, 5))
        self.rowTwo.grid(row=2, column=0, sticky='new', padx=(5, 5))

        store.subscribe(self.__handleStoreUpdate)


    def __handleStoreUpdate(self):
        meState = thaw(store.get_state()['musicEngine'])

        if meState['transposeIncrement'] != self.transposeIncrement.getValue():
            self.transposeIncrement.setValue(meState['transposeIncrement'])
        if meState['inversionRange'] != self.inversionRange.getValue():
            self.inversionRange.setValue(meState['inversionRange'])
        if meState['bassRange'] != self.bassRange.getValue():
            self.bassRange.setValue(meState['bassRange'])
        if meState['chordEngineControl'] != self.controlMode.getValue():
            self.controlMode.setValue(meState['controlMode'])

    def setTransposeIncrement(self, increment):
        store.dispatch(meActions.changeTransposeIncrement(increment))
        settingsStorageUtility.saveSettings()
    
    def setInversionRange(self, range):
        store.dispatch(meActions.changeInversionRange(range))
        settingsStorageUtility.saveSettings

    def setBassRange(self, range):
        store.dispatch(meActions.changeBassRange(range))
        settingsStorageUtility.saveSettings()

    def setControlMode(self, mode):
        store.dispatch(meActions.changeChordEngineControl(mode))
        settingsStorageUtility.saveSettings()
