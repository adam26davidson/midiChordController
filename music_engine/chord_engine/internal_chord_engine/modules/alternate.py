from typing import Callable

from models.app_parameter import AppParameter, AppParameterType
from models.command import Command
from models.command_type import CommandType
from redux import utils as redux_utils

from ...chord_engine_state import state


class Alternate:

    update_chord_engine: Callable

    def __init__(self, update_chord_engine: Callable) -> None:
        self.update_chord_engine = update_chord_engine

        redux_utils.add_app_parameters(self.__get_parameters())

    def set(self, alternate):
        if state.alternate != alternate:
            state.alternate = alternate
            self.update_chord_engine()

    def __get_parameters(self):
        return [
            AppParameter(
                valid_command_types = [CommandType.ON_OFF],
                command_mappings = {
                    Command.ON: lambda: self.set(True),
                    Command.OFF: lambda: self.set(False)
                },
                key = "ALTERNATE",
                label = "Alternate",
                label_abreviation="A",
                type = AppParameterType.INTERNAL_CHORD_ENGINE
            )
        ]
