from typing import Any, Callable

from models.appParameter import AppParameter, AppParameterType
from models.command import Command
from models.commandType import CommandType
from ...chordEngineState import state
from redux import utils as reduxUtils

class Alternate():

    updateChordEngine: Callable

    def __init__(self, updateChordEngine: Callable) -> None:
        self.updateChordEngine = updateChordEngine

        reduxUtils.addAppParameters(self.__getParameters())

    def set(self, alternate):
        if state.alternate != alternate:
            state.alternate = alternate
            self.updateChordEngine()

    def __getParameters(self):
        return [
            AppParameter(
                validCommandTypes = [CommandType.ON_OFF],
                commandMappings = {
                    Command.ON: lambda: self.set(True), 
                    Command.OFF: lambda: self.set(False)
                },
                key = "ALTERNATE",
                label = "Alternate",
                labelAbreviation="A",
                type = AppParameterType.INTERNAL_CHORD_ENGINE
            )
        ]