from __future__ import annotations

from enum import Enum
from typing import Callable

from models.command import Command
from models.commandType import CommandType


class AppParameterType(Enum):
    MUSIC_ENGINE = 1
    CHORD_ENGINE = 2
    INTERNAL_CHORD_ENGINE = 3
    EXTERNAL_CHORD_ENGINE = 4
    UI = 5

class AppParameter:

    validCommandTypes: list[CommandType]
    commandMappings: dict[Command, Callable]
    remappable: bool
    key: str
    label: str
    labelAbreviation: str
    type: AppParameterType

    def __init__(
            self,
            validCommandTypes: list[CommandType],
            commandMappings: dict[Command, Callable],
            key: str,
            label: str | None = None,
            labelAbreviation: str | None = None,
            remappable: bool = True,
            type: AppParameterType = AppParameterType.MUSIC_ENGINE):

        self.commandMappings = commandMappings
        self.validCommandTypes = validCommandTypes
        self.key = key
        self.label = label
        self.labelAbreviation = labelAbreviation
        self.remappable = remappable
        self.type = type
