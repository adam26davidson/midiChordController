from enum import Enum

from .command import Command


class CommandType(Enum):
    ON_OFF = 1
    TOGGLE = 2
    INCREMENTAL = 3
    ANALOG = 4

    def commands(self):
        if self.name == "ON_OFF":
            return [Command.ON, Command.OFF]
        if self.name == "TOGGLE":
            return [Command.TOGGLE]
        if self.name == "INCREMENTAL":
            return [Command.INCREMENT, Command.DECREMENT]
        if self.name == "ANALOG":
            return [Command.UPDATE]
        return []

    def label(self):
        if self.name == "ON_OFF":
            return "On/Off"
        if self.name == "TOGGLE":
            return "Toggle"
        if self.name == "INCREMENTAL":
            return "Increment/Decrement"
        if self.name == "ANALOG":
            return "Analog"
        return "Unknown"
