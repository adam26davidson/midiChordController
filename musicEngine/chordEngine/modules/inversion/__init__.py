from abc import ABC, abstractmethod
import math
from typing import Callable
from constants import INVERSION_SNAP, MAX_INVERSION_RANGE
from models.appParameter import AppParameter, AppParameterType
from models.command import Command
from models.commandType import CommandType
from musicEngine.chordEngine.modules.inversion.inversionState import InversionState
from ...chordEngineState import state
from redux import store
from redux.actions import musicEngine as actions
from redux import utils as reduxUtils
from pyrsistent import thaw

class Inversion(ABC):

    updateChordEngine: Callable
    type: AppParameterType

    def __init__(self, type: AppParameterType, updateChordEngine: Callable):
        self.updateChordEngine = updateChordEngine
        self.type = type

        store.subscribe(self.handleStoreUpdate)

        self.updateReduxRange()
        self.updateReduxValue()

        reduxUtils.addAppParameters(self.getParameters())

    @abstractmethod
    def getState(self) -> InversionState:
        pass

    @abstractmethod
    def updateReduxValue(self):
        pass

    @abstractmethod
    def updateReduxRange(self):
        pass

    @abstractmethod
    def updateReduxLocked(self):
        pass

    @abstractmethod
    def handleStoreUpdate(self):
        pass

    def incrementRange(self):
        self.setRange(self.getState().range + 1)

    def decrementRange(self):
        self.setRange(self.getState().range - 1)

    def setRange(self, range: int):
        range = max(min(range, MAX_INVERSION_RANGE), 0)
        self.getState().range = range
        oldInversion = self.getState().value
        self.getState().value = max(min(oldInversion, range), -1*range)

        self.updateChordEngine()
        self.updateReduxValue()
        self.updateReduxRange()

    def increment(self):
        newInversion = self.getState().value + 1
        if abs(newInversion) <= self.getState().range:
            self.setValue(newInversion)

    def decrement(self):
        newInversion = self.getState().value - 1
        if abs(newInversion) <= self.getState().range:
            self.setValue(newInversion)

    def setValue(self, inversion):
        if (not self.getState().locked):
            if inversion != self.getState().value:
                range = self.getState().range
                self.getState().value = max(min(inversion, range), -1*range)
                self.updateChordEngine()
                self.updateReduxValue()

    def setAnalogValue(self, value):
        inversion = self.processValue(value)
        self.setValue(inversion)

    def toggleLock(self):
        self.getState().locked = not self.getState().locked
        self.updateReduxLocked()

    def processValue(self, rawValue):
        maxSteps = self.getState().range
        lastValue = self.getState().value

        # converts to an integer in the correct inversion range
        def getValue(x):
            return math.floor(((x+1)/2)*((2*maxSteps)+1)) - maxSteps

        # snap processed value back into current window if within snap region
        value = getValue(rawValue)
        snap = (1.0 / (maxSteps + 1)) * INVERSION_SNAP
        if value == lastValue + 1:
            rawValue -= snap
            value = getValue(rawValue)
        if value == lastValue - 1:
            rawValue += snap
            value = getValue(rawValue)

        return value

    

