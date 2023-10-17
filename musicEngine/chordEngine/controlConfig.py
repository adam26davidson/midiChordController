from ...models.appParameter import AppParameter
from ...models.commandType import CommandType
from ...models.commandMapping import CommandMapping
from ...models.command import Command
from .controlState import ChordButton


controlConfig = [
    AppParameter(
        validCommandTypes = [CommandType.ON_OFF],
        commandMappings = [
            CommandMapping(Command.ON, ), 
            CommandMapping(Command.OFF, lambda: self.chordEngine.chordButtonOn(ChordButton.SOUTH))],
    )
]
