from models.appParameter import AppParameter, AppParameterType
from models.command import Command
from models.commandType import CommandType
from musicEngine.chordEngine.modules.inversion import Inversion
from musicEngine.chordEngine.state.inversionState import InversionState
from redux import store
from redux.actions import musicEngine as actions
from ...chordEngineState import state
from pyrsistent import thaw

class BassPosition(Inversion):
        
    def __init__(self, type: AppParameterType, updateChordEngine: callable):
        super().__init__(type, updateChordEngine)

    def getState(self) -> InversionState:
        return state.bassPosition

    def updateReduxValue(self):
        store.dispatch(actions.changeBassPosition(state.bassPosition.value))

    def updateReduxRange(self):
        store.dispatch(actions.changeBassRange(state.bassPosition.range))

    def updateReduxLocked(self):
        pass

    def handleStoreUpdate(self):
        meState = thaw(store.get_state()['musicEngine'])
        if (meState['bassRange'] != state.bassPosition.range):
            self.setRange(meState['bassRange'])

    def getParameters(self):
        keyPrefix = "EXTERNAL_" if self.type == AppParameterType.EXTERNAL_CHORD_ENGINE else "INTERNAL_"        
        return [
            AppParameter(
                validCommandTypes = [CommandType.ANALOG, CommandType.INCREMENTAL],
                commandMappings = {
                    Command.UPDATE: self.setAnalogValue,
                    Command.INCREMENT: self.increment,
                    Command.DECREMENT: self.decrement
                },
                key = f"{keyPrefix}BASS_POSITION",
                label = "Bass Position",
                labelAbreviation="BP",
                type = self.type
            ),
            AppParameter(
                validCommandTypes = [CommandType.TOGGLE],
                commandMappings = {
                    Command.TOGGLE: self.toggleLock
                },
                key = f"{keyPrefix}BASS_POSITION_LOCK",
                label = "Bass Position Lock",
                labelAbreviation="BL",
                type = self.type
            ),
            AppParameter(
                validCommandTypes = [CommandType.INCREMENTAL],
                commandMappings = {
                    Command.INCREMENT: self.incrementRange,
                    Command.DECREMENT: self.decrementRange
                },
                key = f"{keyPrefix}BASS_POSITION_RANGE",
                label = "Bass Range",
                labelAbreviation="BR",
                type = self.type
            )
        ]