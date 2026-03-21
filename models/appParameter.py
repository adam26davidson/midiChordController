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

    valid_command_types: list[CommandType]
    command_mappings: dict[Command, Callable]
    remappable: bool
    key: str
    label: str
    label_abreviation: str
    type: AppParameterType

    def __init__(
            self,
            valid_command_types: list[CommandType],
            command_mappings: dict[Command, Callable],
            key: str,
            label: str | None = None,
            label_abreviation: str | None = None,
            remappable: bool = True,
            type: AppParameterType = AppParameterType.MUSIC_ENGINE):

        self.command_mappings = command_mappings
        self.valid_command_types = valid_command_types
        self.key = key
        self.label = label
        self.label_abreviation = label_abreviation
        self.remappable = remappable
        self.type = type
