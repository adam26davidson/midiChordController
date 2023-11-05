from models.appParameter import AppParameter, AppParameterType
from models.command import Command
from models.commandType import CommandType
from musicEngine.chordEngine.modules.inversion import Inversion
from musicEngine.chordEngine.modules.inversion.inversionState import InversionState
from redux import store
from redux.actions import musicEngine as actions
from ...chordEngineState import state
from pyrsistent import thaw

class ChordInversion(Inversion):

    def __init__(self, type: AppParameterType, updateChordEngine: callable):
        super().__init__(type, updateChordEngine)

    def getState(self) -> InversionState:
        return state.inversion

    def updateReduxValue(self):
        store.dispatch(actions.changeInversion(state.inversion.value))

    def updateReduxRange(self):
        store.dispatch(actions.changeInversionRange(state.inversion.range))

    def updateReduxLocked(self):
        store.dispatch(actions.changeInversionLock(state.inversion.locked))

    def handleStoreUpdate(self):
        meState = thaw(store.get_state()['musicEngine'])
        if (meState['inversionRange'] != state.inversion.range):
            self.setRange(meState['inversionRange'])

    def getParameters(self):
        return [
            AppParameter(
                validCommandTypes = [CommandType.ANALOG, CommandType.INCREMENTAL],
                commandMappings = {
                    Command.UPDATE: self.setAnalogValue,
                    Command.INCREMENT: self.increment,
                    Command.DECREMENT: self.decrement
                },
                key = "INVERSION",
                label = "Inversion",
                labelAbreviation="I",
                type = self.type
            ),
            AppParameter(
                validCommandTypes = [CommandType.TOGGLE],
                commandMappings = {
                    Command.TOGGLE: self.toggleLock
                },
                key = "INVERSION_LOCK",
                label = "Inversion Lock",
                labelAbreviation="IL",
                type = self.type
            ),
            AppParameter(
                validCommandTypes = [CommandType.INCREMENTAL],
                commandMappings = {
                    Command.INCREMENT: self.incrementRange,
                    Command.DECREMENT: self.decrementRange
                },
                key = "INVERSION_RANGE",
                label = "Inversion Range",
                labelAbreviation="IR",
            )
        ]