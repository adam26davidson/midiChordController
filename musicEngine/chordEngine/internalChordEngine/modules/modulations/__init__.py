from typing import Callable

from models.appParameter import AppParameter, AppParameterType
from models.command import Command
from models.commandType import CommandType
from musicEngine.chordEngine.internalChordEngine.modules.modulations.modulation import Modulation
from redux import store
from redux import utils as reduxUtils
from redux.actions import musicEngine as actions

from ....chordEngineState import state
from ....state.modulationsState import ModulationSide


class Modulations:

    dict: dict[ModulationSide, Modulation]
    updateChordEngine: Callable

    def __init__(self, setting: dict, updateChordEngine: Callable):
        self.updateChordEngine = updateChordEngine
        self.dict = {
            ModulationSide.LEFT: Modulation(state.scale.keyAgnostic, setting["left"]),
            ModulationSide.RIGHT: Modulation(state.scale.keyAgnostic, setting["right"])
        }

        reduxUtils.addAppParameters(self.__getParameters())

    def get(self, side: ModulationSide = None) -> Modulation:
        if side:
            return self.dict[side]
        if state.modulation.side == ModulationSide.NONE:
            return None
        return self.dict[state.modulation.side]

    def apply(self, notes: list[int], scale: list[int]) -> list[int]:
        modulation = self.get()
        if modulation:
            return modulation.apply(notes, scale)
        return notes

    def applyOne(self, note: int, scale: list[int]) -> int:
        modulation = self.get()
        if modulation:
            return modulation.applyOne(note, scale)
        return note

    def set(self, side: ModulationSide):
        if state.modulation.side != side:
            scale = state.scale.keyAgnostic
            if side != ModulationSide.NONE:
                scale = self.get(side).applyToScale()

            store.dispatch(actions.changeModulation({
                'scale': scale,
                'side': side
            }))

            state.modulation.side = side
            self.updateChordEngine()

    def __getParameters(self):
        return [
            AppParameter(
                validCommandTypes = [CommandType.ON_OFF],
                commandMappings = {
                    Command.ON: lambda: self.set(ModulationSide.LEFT),
                    Command.OFF: lambda: self.set(ModulationSide.NONE)
                },
                key = "LEFT_MODULATION",
                label = "Modulation 1",
                labelAbreviation="M1",
                type = AppParameterType.INTERNAL_CHORD_ENGINE
            ),
            AppParameter(
                validCommandTypes = [CommandType.ON_OFF],
                commandMappings = {
                    Command.ON: lambda: self.set(ModulationSide.RIGHT),
                    Command.OFF: lambda: self.set(ModulationSide.NONE)
                },
                key = "RIGHT_MODULATION",
                label = "Modulation 2",
                labelAbreviation="M2",
                type = AppParameterType.INTERNAL_CHORD_ENGINE
            )
        ]
