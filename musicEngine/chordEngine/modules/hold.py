from typing import Callable
from models.appParameter import AppParameter, AppParameterType
from models.command import Command
from models.commandType import CommandType
from redux import store
from redux.actions import musicEngine as actions
from ..chordEngineState import state
from redux import utils as reduxUtils


class Hold():

    stopChordAndBass: Callable
    type: AppParameterType
    
    def __init__(self, type: AppParameterType, stopChordAndBass: Callable):
        self.stopChordAndBass = stopChordAndBass
        self.type = type

        store.dispatch(actions.changeHold(state.hold))
        reduxUtils.addAppParameters(self.__getParameters())


    def toggle(self):
        if state.hold:
            state.hold = False
            self.stopChordAndBass()
        else:
            state.hold = True
        store.dispatch(actions.changeHold(state.hold))

    def __getParameters(self):
        keyPrefix = "EXTERNAL_" if self.type == AppParameterType.EXTERNAL_CHORD_ENGINE else "INTERNAL_"
        return [
            AppParameter(
                validCommandTypes = [CommandType.TOGGLE],
                commandMappings = {
                    Command.TOGGLE: self.toggle
                },
                key = f"{keyPrefix}HOLD",
                label = "Hold",
                labelAbreviation="H",
                type = self.type
            )
        ]