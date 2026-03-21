"""Tests for InternalChordEngine: settings cycling, chord generation, modulations."""

import music_engine.chord_engine.chord_engine_state as state_module
from music_engine.chord_engine.internal_chord_engine import InternalChordEngine
from music_engine.chord_engine.state.chords_state import ChordButton
from music_engine.chord_engine.state.modulations_state import ModulationSide


def make_engine():
    engine = InternalChordEngine()
    engine.callbacks = []
    return engine


class TestLoadSetting:
    def test_load_default_preset_scale(self):
        engine = make_engine()
        engine.load_setting(0)
        assert state_module.state.scale.key_agnostic == [0, 2, 4, 5, 7, 9, 11]

    def test_load_default_preset_has_four_chords(self):
        engine = make_engine()
        engine.load_setting(0)
        assert len(engine.chords) == 4
        assert set(engine.chords.keys()) == {
            ChordButton.SOUTH,
            ChordButton.WEST,
            ChordButton.NORTH,
            ChordButton.EAST,
        }

    def test_load_setting_updates_index(self):
        engine = make_engine()
        engine.load_setting(3)
        assert state_module.state.internal_settings.index == 3

    def test_load_setting_clears_loading_flag(self):
        engine = make_engine()
        engine.load_setting(0)
        assert state_module.state.internal_settings.loading is False


class TestIncrementSetting:
    def test_increment_advances_index(self):
        engine = make_engine()
        assert state_module.state.internal_settings.index == 0
        engine.increment_setting()
        assert state_module.state.internal_settings.index == 1

    def test_increment_cycles_through_all_presets(self):
        engine = make_engine()
        indices = [state_module.state.internal_settings.index]
        for _ in range(8):
            engine.increment_setting()
            indices.append(state_module.state.internal_settings.index)
        # Should cycle 0 -> 1 -> 2 -> ... -> 7 -> 0
        assert indices == [0, 1, 2, 3, 4, 5, 6, 7, 0]

    def test_increment_wraps_from_last_to_first(self):
        engine = make_engine()
        engine.load_setting(7)
        engine.increment_setting()
        assert state_module.state.internal_settings.index == 0


class TestDecrementSetting:
    def test_decrement_wraps_from_first_to_last(self):
        engine = make_engine()
        assert state_module.state.internal_settings.index == 0
        engine.decrement_setting()
        assert state_module.state.internal_settings.index == 7

    def test_decrement_cycles_backwards(self):
        engine = make_engine()
        indices = [state_module.state.internal_settings.index]
        for _ in range(8):
            engine.decrement_setting()
            indices.append(state_module.state.internal_settings.index)
        # 0 -> 7 -> 6 -> 5 -> 4 -> 3 -> 2 -> 1 -> 0
        assert indices == [0, 7, 6, 5, 4, 3, 2, 1, 0]

    def test_decrement_from_middle(self):
        engine = make_engine()
        engine.load_setting(4)
        engine.decrement_setting()
        assert state_module.state.internal_settings.index == 3


class TestGetChordNotes:
    def test_south_chord_returns_notes(self):
        engine = make_engine()
        notes = engine.get_chord_notes(ChordButton.SOUTH)
        assert isinstance(notes, list)
        assert len(notes) > 0

    def test_south_chord_notes_are_valid_midi(self):
        engine = make_engine()
        notes = engine.get_chord_notes(ChordButton.SOUTH)
        for note in notes:
            assert 0 <= note <= 127

    def test_south_chord_pitch_classes_are_c_major(self):
        """Default south chord is C major 7th: scale degrees [0,2,4,6] on
        C major scale [0,2,4,5,7,9,11] => pitch classes C(0), E(4), G(7), B(11)."""
        engine = make_engine()
        notes = engine.get_chord_notes(ChordButton.SOUTH)
        pitch_classes = sorted({n % 12 for n in notes})
        # C major 7th pitch classes
        assert 0 in pitch_classes   # C
        assert 4 in pitch_classes   # E
        assert 7 in pitch_classes   # G

    def test_different_buttons_produce_different_notes(self):
        engine = make_engine()
        south = engine.get_chord_notes(ChordButton.SOUTH)
        west = engine.get_chord_notes(ChordButton.WEST)
        assert south != west


class TestGetBassNote:
    def test_bass_note_is_valid_midi(self):
        engine = make_engine()
        bass = engine.get_bass_note()
        assert isinstance(bass, int)
        assert 0 <= bass <= 127

    def test_bass_note_for_south_is_c(self):
        """Default south chord bass should be rooted on C (pitch class 0)."""
        engine = make_engine()
        state_module.state.chord.active_button = ChordButton.SOUTH
        bass = engine.get_bass_note()
        assert bass % 12 == 0


class TestGetChordNoteClasses:
    def test_returns_pitch_classes_and_root(self):
        engine = make_engine()
        pitch_classes, root_class = engine.get_chord_note_classes()
        assert isinstance(pitch_classes, list)
        assert isinstance(root_class, int)

    def test_default_south_root_is_c(self):
        engine = make_engine()
        state_module.state.chord.active_button = ChordButton.SOUTH
        _pitch_classes, root_class = engine.get_chord_note_classes()
        assert root_class == 0

    def test_default_south_pitch_classes(self):
        """C major 7th: C(0), E(4), G(7), B(11)."""
        engine = make_engine()
        state_module.state.chord.active_button = ChordButton.SOUTH
        pitch_classes, _root = engine.get_chord_note_classes()
        assert sorted(pitch_classes) == [0, 4, 7, 11]


class TestModulationEffect:
    def test_modulation_left_changes_chord_output(self):
        engine = make_engine()
        # Get unmodulated chord
        notes_none = engine.get_chord_notes(ChordButton.SOUTH)
        classes_none = sorted({n % 12 for n in notes_none})

        # Activate left modulation
        engine.modulations.set(ModulationSide.LEFT)
        notes_left = engine.get_chord_notes(ChordButton.SOUTH)
        classes_left = sorted({n % 12 for n in notes_left})

        assert classes_left != classes_none

    def test_modulation_right_changes_chord_output(self):
        engine = make_engine()
        notes_none = engine.get_chord_notes(ChordButton.SOUTH)
        classes_none = sorted({n % 12 for n in notes_none})

        engine.modulations.set(ModulationSide.RIGHT)
        notes_right = engine.get_chord_notes(ChordButton.SOUTH)
        classes_right = sorted({n % 12 for n in notes_right})

        assert classes_right != classes_none

    def test_modulation_none_leaves_chord_unmodulated(self):
        engine = make_engine()
        state_module.state.modulation.side = ModulationSide.NONE
        notes = engine.get_chord_notes(ChordButton.SOUTH)
        pitch_classes = sorted({n % 12 for n in notes})
        # Unmodulated south chord is C major 7th
        assert 0 in pitch_classes   # C
        assert 4 in pitch_classes   # E
        assert 7 in pitch_classes   # G

    def test_returning_to_none_restores_original(self):
        engine = make_engine()
        notes_before = engine.get_chord_notes(ChordButton.SOUTH)

        engine.modulations.set(ModulationSide.LEFT)
        engine.modulations.set(ModulationSide.NONE)

        notes_after = engine.get_chord_notes(ChordButton.SOUTH)
        assert sorted(notes_before) == sorted(notes_after)
