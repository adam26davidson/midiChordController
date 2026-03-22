from __future__ import annotations

from models.app_parameter import AppParameter
from models.command import Command
from models.command_type import CommandType
from music_engine.chord_engine.external_chord_engine import ExternalChordEngine
from music_engine.chord_engine.internal_chord_engine import InternalChordEngine
from redux import store
from redux import utils as redux_utils
from redux.actions import controller_coupler as cc_actions

from .midi import Midi
from .rhythm_engine import RhythmEngine


class MusicEngine:

    def __init__(self) -> None:
        self.internal_chord_engine = InternalChordEngine()
        self.external_chord_engine = ExternalChordEngine()
        self.rhythm_engine = RhythmEngine()
        self.midi = Midi()

        self.process_controller_events: bool = True

        self.midi.subscribe(self.external_chord_engine.handle_midi_message)
        self.internal_chord_engine.subscribe(self.rhythm_engine.handle_message)
        self.external_chord_engine.subscribe(self.rhythm_engine.handle_message)
        self.rhythm_engine.subscribe(self.midi.handle_message)

        redux_utils.add_app_parameters(self.get_parameters())

        store.dispatch(cc_actions.music_engine_app_parameters_loaded())

    def start(self) -> None:
        self.external_chord_engine.start()
        self.midi.start()

    def get_parameters(self) -> list[AppParameter]:
        parameters: list[AppParameter] = [
            AppParameter(
                valid_command_types = [CommandType.ANALOG],
                command_mappings = {
                    Command.UPDATE: self.midi.set_after_touch
                },
                key = "AFTERTOUCH",
                label = "Aftertouch",
                label_abreviation="AT",
            )
        ]

        for cc in range(1, 128):
            parameters.append(
                AppParameter(
                    valid_command_types = [CommandType.ANALOG],
                    command_mappings = {
                        Command.UPDATE: self.midi.get_cc_setter(cc)
                    },
                    key = f"MIDI_CC_{cc}",
                    label = f"MIDI CC {cc}",
                    label_abreviation=f"CC{cc}",
                )
            )

        return parameters
