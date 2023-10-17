from models.commandType import CommandType
from models.command import Command
from typing import Callable, Dict

class AppParameter():

    validCommandTypes: list[CommandType]
    commandMappings: Dict[Command, Callable]
    remappable: bool
    key: str
    label: str
    labelAbreviation: str

    def __init__(
            self, 
            validCommandTypes: list[CommandType], 
            commandMappings: Dict[Command, Callable], 
            key: str, 
            label: str, 
            labelAbreviation: str,
            remappable: bool = True):
        
        self.commandMappings = commandMappings
        self.validCommandTypes = validCommandTypes
        self.key = key
        self.label = label
        self.labelAbreviation = labelAbreviation
        self.remappable = remappable