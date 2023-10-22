from enum import Enum
from models.commandType import CommandType
from models.command import Command
from typing import Callable, Dict, List

class AppParemeterType(Enum):
    MUSIC_ENGINE = 1
    UI = 2

class AppParameter():

    validCommandTypes: List[CommandType]
    commandMappings: Dict[Command, Callable]
    remappable: bool
    key: str
    label: str
    labelAbreviation: str
    type: AppParemeterType

    def __init__(
            self, 
            validCommandTypes: List[CommandType], 
            commandMappings: Dict[Command, Callable], 
            key: str, 
            label: str = None, 
            labelAbreviation: str = None,
            remappable: bool = True,
            type: AppParemeterType = AppParemeterType.MUSIC_ENGINE):
        
        self.commandMappings = commandMappings
        self.validCommandTypes = validCommandTypes
        self.key = key
        self.label = label
        self.labelAbreviation = labelAbreviation
        self.remappable = remappable
        type = type