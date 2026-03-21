from typing import Callable

from models.appParameter import AppParameter, AppParameterType
from models.command import Command
from models.commandType import CommandType
from musicEngine.chordEngine.internalChordEngine.modules.modulations.modulation import Modulation
from redux import store
from redux import utils as redux_utils
from redux.actions import musicEngine as actions

from ....chordEngineState import state
from ....state.modulationsState import ModulationSide


class Modulations:

    dict: dict[ModulationSide, Modulation]
    update_chord_engine: Callable

    def __init__(self, setting: dict, update_chord_engine: Callable):
        self.update_chord_engine = update_chord_engine
        self.dict = {
            ModulationSide.LEFT: Modulation(state.scale.key_agnostic, setting["left"]),
            ModulationSide.RIGHT: Modulation(state.scale.key_agnostic, setting["right"])
        }

        redux_utils.add_app_parameters(self.__get_parameters())

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

    def apply_one(self, note: int, scale: list[int]) -> int:
        modulation = self.get()
        if modulation:
            return modulation.apply_one(note, scale)
        return note

    def set(self, side: ModulationSide):
        if state.modulation.side != side:
            scale = state.scale.key_agnostic
            if side != ModulationSide.NONE:
                scale = self.get(side).apply_to_scale()

            store.dispatch(actions.change_modulation({
                'scale': scale,
                'side': side
            }))

            state.modulation.side = side
            self.update_chord_engine()

    def __get_parameters(self):
        return [
            AppParameter(
                valid_command_types = [CommandType.ON_OFF],
                command_mappings = {
                    Command.ON: lambda: self.set(ModulationSide.LEFT),
                    Command.OFF: lambda: self.set(ModulationSide.NONE)
                },
                key = "LEFT_MODULATION",
                label = "Modulation 1",
                label_abreviation="M1",
                type = AppParameterType.INTERNAL_CHORD_ENGINE
            ),
            AppParameter(
                valid_command_types = [CommandType.ON_OFF],
                command_mappings = {
                    Command.ON: lambda: self.set(ModulationSide.RIGHT),
                    Command.OFF: lambda: self.set(ModulationSide.NONE)
                },
                key = "RIGHT_MODULATION",
                label = "Modulation 2",
                label_abreviation="M2",
                type = AppParameterType.INTERNAL_CHORD_ENGINE
            )
        ]
