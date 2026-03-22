from __future__ import annotations

from typing import TYPE_CHECKING

from models.app_parameter import AppParameter, AppParameterType

if TYPE_CHECKING:
    from collections.abc import Callable
from models.command import Command
from models.command_type import CommandType
from music_engine.chord_engine.internal_chord_engine.modules.secondaries.parse_secondaries import parse_secondaries
from music_engine.chord_engine.internal_chord_engine.modules.secondaries.secondary import Secondary  # noqa: F401
from music_engine.chord_engine.modules.chords.dual_chord import DualChord
from music_engine.chord_engine.state.chords_state import ChordButton
from music_engine.chord_engine.state.modulations_state import ModulationSide
from music_engine.chord_engine.state.secondaries_state import SecondarySide
from redux import utils as redux_utils

from ....chord_engine_state import state


class Secondaries:

    dict: dict[SecondarySide, dict[ChordButton, dict[ModulationSide, DualChord]]]
    update_chord_engine: Callable[[], None]

    def __init__(self, setting: dict, update_chord_engine: Callable[[], None]) -> None:
        self.dict = parse_secondaries(setting)
        self.update_chord_engine = update_chord_engine

        redux_utils.add_app_parameters(self.__get_parameters())

    def set(self, side: SecondarySide) -> None:
        if state.secondary.side != side:
            state.secondary.side = side
            self.update_chord_engine()

    def get_chord(self, chord_root: int) -> list[int] | None:
        secondary = self.get()
        return None if secondary is None else secondary.get_chord(chord_root)

    def get_bass(self, chord_root: int) -> int | None:
        secondary = self.get()
        return None if secondary is None else secondary.get_bass(chord_root)

    def get_root(self, chord_root: int) -> int | None:
        secondary = self.get()
        return None if secondary is None else secondary.get_root(chord_root)

    def get_note_types(self, chord_root: int) -> list[int] | None:
        secondary = self.get()
        return None if secondary is None else secondary.get_note_types(chord_root)

    def get(self, button: ChordButton | None = None) -> DualChord | None:
        if button is None:
            button = state.chord.active_button

        if state.secondary.side == SecondarySide.NONE:
            return None
        return self.dict[state.secondary.side][button][state.modulation.side]

    def __get_parameters(self) -> list[AppParameter]:
        return [
            AppParameter(
                valid_command_types = [CommandType.ON_OFF],
                command_mappings = {
                    Command.ON: lambda: self.set(SecondarySide.LEFT),
                    Command.OFF: lambda: self.set(SecondarySide.NONE)
                },
                key = "LEFT_SECONDARY",
                label = "Secondary 1",
                label_abreviation="S1",
                type = AppParameterType.INTERNAL_CHORD_ENGINE
            ),
            AppParameter(
                valid_command_types = [CommandType.ON_OFF],
                command_mappings = {
                    Command.ON: lambda: self.set(SecondarySide.RIGHT),
                    Command.OFF: lambda: self.set(SecondarySide.NONE)
                },
                key = "RIGHT_SECONDARY",
                label = "Secondary 2",
                label_abreviation="S2",
                type = AppParameterType.INTERNAL_CHORD_ENGINE
            )
        ]
