from typing import Callable, Dict
from models.appParameter import AppParameter, AppParameterType
from models.command import Command
from models.commandType import CommandType
from musicEngine.chordEngine.state.modulationsState import ModulationSide
from musicEngine.chordEngine.internalChordEngine.modules.secondaries.parseSecondaries import parseSecondaries
from musicEngine.chordEngine.state.secondariesState import SecondarySide
from musicEngine.chordEngine.internalChordEngine.modules.secondaries.secondary import Secondary
from musicEngine.chordEngine.state.chordsState import ChordButton
from musicEngine.chordEngine.modules.chords.dualChord import DualChord
from ....chordEngineState import state
from redux import utils as reduxUtils


class Secondaries():

    dict: Dict[SecondarySide, Dict[ChordButton, Dict[ModulationSide, DualChord]]]
    updateChordEngine: Callable
    
    def __init__(self, setting: dict, updateChordEngine: Callable) -> None:
        self.dict = parseSecondaries(setting)
        self.updateChordEngine = updateChordEngine

        reduxUtils.addAppParameters(self.__getParameters())

    def set(self, side):
        if state.secondary.side != side:
            state.secondary.side = side
            self.updateChordEngine()

    def getChord(self, chordRoot: int) -> list[int]:
        secondary = self.get()
        return None if secondary == None else secondary.getChord(chordRoot)

    def getBass(self, chordRoot: int) -> int:
        secondary = self.get()
        return None if secondary == None else secondary.getBass(chordRoot)
        
    def getRoot(self, chordRoot: int) -> int:
        secondary = self.get()
        return None if secondary == None else secondary.getRoot(chordRoot)
        
    def getNoteTypes(self, chordRoot: int) -> list[int]:
        secondary = self.get()
        return None if secondary == None else secondary.getNoteTypes(chordRoot)
    
    def get(self, button: ChordButton = None) -> DualChord:
        if button == None:
            button = state.chord.activeButton

        if state.secondary.side == SecondarySide.NONE:
            return None
        return self.dict[state.secondary.side][button][state.modulation.side]
    
    def __getParameters(self):
        return [
            AppParameter(
                validCommandTypes = [CommandType.ON_OFF],
                commandMappings = {
                    Command.ON: lambda: self.set(SecondarySide.LEFT), 
                    Command.OFF: lambda: self.set(SecondarySide.NONE)
                },
                key = "LEFT_SECONDARY",
                label = "Secondary 1",
                labelAbreviation="S1",
                type = AppParameterType.INTERNAL_CHORD_ENGINE
            ),
            AppParameter(
                validCommandTypes = [CommandType.ON_OFF],
                commandMappings = {
                    Command.ON: lambda: self.set(SecondarySide.RIGHT),
                    Command.OFF: lambda: self.set(SecondarySide.NONE)
                },
                key = "RIGHT_SECONDARY",
                label = "Secondary 2",
                labelAbreviation="S2",
                type = AppParameterType.INTERNAL_CHORD_ENGINE
            )
        ]
    
