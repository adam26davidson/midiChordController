from __future__ import annotations

from constants import SETTINGS
from models.app_parameter import AppParameter, AppParameterType
from models.command import Command
from models.command_type import CommandType
from music_engine.chord_engine.chord_engine import ChordEngine
from music_engine.chord_engine.internal_chord_engine.modules.alternate import Alternate
from music_engine.chord_engine.internal_chord_engine.modules.modulations import Modulations
from music_engine.chord_engine.internal_chord_engine.modules.secondaries import Secondaries
from music_engine.chord_engine.state.secondaries_state import SecondarySide
from redux import store
from redux import utils as redux_utils
from redux.actions import music_engine as actions

from ..chord_engine_state import state
from ..modules.chords.dual_chord import DualChord
from ..state.chords_state import ChordButton


class InternalChordEngine(ChordEngine):

    modulations: Modulations

    def __init__(self) -> None:
        super().__init__(AppParameterType.INTERNAL_CHORD_ENGINE)

        self.alternate = Alternate(self.update_chord_type)
        store.dispatch(actions.change_settings_list([s['name'] for s in SETTINGS]))
        self.load_setting(state.internal_settings.index)

        redux_utils.add_app_parameters(self.get_internal_parameters())

    def increment_setting(self) -> None:
        self.load_setting((state.internal_settings.index + 1) % len(SETTINGS))

    def decrement_setting(self) -> None:
        new_index = state.internal_settings.index - 1
        if (new_index < 0):
            new_index = len(SETTINGS) - 1
        self.load_setting(new_index)

    def load_setting(self, index: int) -> None:
        state.internal_settings.loading = True
        store.dispatch(actions.change_setting_loading(True))

        self.stop_chord_and_bass()

        state.internal_settings.index = index
        setting = SETTINGS[index]

        self.scale.update(setting['scale'])

        self.chords = {
            ChordButton.SOUTH: DualChord(setting["chords"][ChordButton.SOUTH.value], state.scale.key_agnostic),
            ChordButton.WEST: DualChord(setting["chords"][ChordButton.WEST.value], state.scale.key_agnostic),
            ChordButton.NORTH: DualChord(setting["chords"][ChordButton.NORTH.value], state.scale.key_agnostic),
            ChordButton.EAST: DualChord(setting["chords"][ChordButton.EAST.value], state.scale.key_agnostic)
        }

        self.secondaries = Secondaries(setting["secondaries"], self.update_chord_type)
        self.modulations = Modulations(setting["modulations"], self.update_chord_type)

        state.chord.note_classes, state.chord.root_class = self.get_chord_note_classes()

        store.dispatch(actions.change_setting(index))
        store.dispatch(actions.change_chord_type({
            'chord': state.chord.note_classes,
            'root': state.chord.root_class
        }))
        shadow_chord = self.get_chord_notes(state.chord.active_button)
        store.dispatch(actions.change_chord_shadow(shadow_chord))
        store.dispatch(actions.change_bass_shadow(self.get_bass_note()))

        store.dispatch(actions.change_setting_loading(False))
        state.internal_settings.loading = False

    def get_chord_note_classes(self) -> tuple[list[int], int]:
        chord = self.chords[state.chord.active_button]
        scale = self.scale.get()
        if (state.secondary.side == SecondarySide.NONE):
            root_type = self.modulations.apply_one(chord.get_root(), scale)
            modulated_types = self.modulations.apply(chord.get_note_types(), scale)
            return [note % 12 for note in modulated_types], root_type % 12
        chord_root = self.modulations.apply_one(chord.get_root(), scale)
        root_type = self.secondaries.get_root(chord_root)
        chord_type = self.secondaries.get_note_types(chord_root)
        assert chord_type is not None
        assert root_type is not None
        chord_type.sort()
        return chord_type, root_type

    def get_chord_notes(self, button: ChordButton) -> list[int]:
        chord = self.chords[button]
        chord_notes = []

        if (state.secondary.side == SecondarySide.NONE):
            modless_chord = chord.get_chord()
            chord_notes = self.modulations.apply(modless_chord, self.scale.get())
        else:
            modulated_root = self.modulations.apply_one(chord.get_root(), self.scale.get())
            chord_notes = self.secondaries.get_chord(modulated_root)

        assert chord_notes is not None
        chord_adjusted_octaves = self.chord_octave.apply(chord_notes)
        return chord_adjusted_octaves

    def get_bass_note(self) -> int:
        chord = self.chords[state.chord.active_button]

        if (state.secondary.side == SecondarySide.NONE):
            bass = chord.get_bass()
            return self.modulations.apply_one(bass, self.scale.get())
        chord_root = self.modulations.apply_one(chord.get_root(), self.scale.get())
        bass = self.secondaries.get_bass(chord_root)
        assert bass is not None
        return bass

    def get_internal_parameters(self) -> list[AppParameter]:
        return [
            AppParameter(
                valid_command_types = [CommandType.INCREMENTAL],
                command_mappings = {
                    Command.INCREMENT: self.increment_setting,
                    Command.DECREMENT: self.decrement_setting
                },
                key = "SETTING",
                label = "Patch",
                label_abreviation="P",
                type = AppParameterType.INTERNAL_CHORD_ENGINE
            )
        ]
