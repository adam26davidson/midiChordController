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
        elif self.name == "TOGGLE":
            return [Command.TOGGLE]
        elif self.name == "INCREMENTAL":
            return [Command.INCREMENT, Command.DECREMENT]
        elif self.name == "ANALOG":
            return [Command.UPDATE]
        else:
            return []
        
    def label(self):
        if self.name == "ON_OFF":
            return "On/Off"
        elif self.name == "TOGGLE":
            return "Toggle"
        elif self.name == "INCREMENTAL":
            return "Increment/Decrement"
        elif self.name == "ANALOG":
            return "Analog"
        else:
            return "Unknown"