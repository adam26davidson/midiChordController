"""Tests for Secondary class and parse_secondaries."""

import music_engine.chord_engine.chord_engine_state as state_module
from music_engine.chord_engine.internal_chord_engine.modules.secondaries.parse_secondaries import (
    parse_secondaries,
)
from music_engine.chord_engine.internal_chord_engine.modules.secondaries.secondary import Secondary
from music_engine.chord_engine.state.chords_state import ChordButton
from music_engine.chord_engine.state.modulations_state import ModulationSide
from music_engine.chord_engine.state.secondaries_state import SecondarySide


class TestSecondary:
    """Secondary is a Chord subclass that uses interval-based transposition."""

    def test_get_root_with_interval(self):
        # interval=3, target_root=0 → (0+3)%12 = 3
        sec = Secondary([0, 4, 7], [0], 3)
        assert sec.get_root(0) == 3

    def test_get_root_wraps(self):
        sec = Secondary([0, 4, 7], [0], 10)
        # target_root=5 → (5+10)%12 = 3
        assert sec.get_root(5) == 3

    def test_get_note_for_key_is_chromatic(self):
        # Secondary overrides get_note_for_key to be purely chromatic: (note + key) % 12
        sec = Secondary([0, 4, 7], [0], 0)
        assert sec.get_note_for_key(4, 3) == 7  # (4+3)%12

    def test_get_chord_returns_notes(self):
        sec = Secondary([0, 4, 7], [0], 0)
        state_module.state.voice_count = 3
        chord = sec.get_chord(0)
        assert len(chord) == 3
        assert all(21 <= n <= 108 for n in chord)

    def test_get_chord_with_transposition(self):
        sec = Secondary([0, 4, 7], [0], 3)
        state_module.state.voice_count = 3
        chord = sec.get_chord(0)
        # Root is (0+3)%12=3, so pitch classes should be Eb major: 3, 7, 10
        pitch_classes = sorted({n % 12 for n in chord})
        assert pitch_classes == [3, 7, 10]

    def test_get_bass_pitch_class(self):
        sec = Secondary([0, 4, 7], [0], 0)
        bass = sec.get_bass(0)
        assert 21 <= bass <= 108
        assert bass % 12 == 0  # Root at interval 0 from target 0 = C


class TestParseSecondaries:
    def _make_secondary_setting(self):
        return {
            "left": {
                "interval": 1,
                "main": [0, 4, 7],
                "mainBass": [0],
                "alternate": [0, 3, 7],
                "alternateBass": [0],
            },
            "right": {
                "interval": 2,
                "main": [0, 4, 7],
                "mainBass": [0],
                "alternate": [0, 3, 7],
                "alternateBass": [0],
            },
        }

    def test_returns_both_sides(self):
        result = parse_secondaries(self._make_secondary_setting())
        assert SecondarySide.LEFT in result
        assert SecondarySide.RIGHT in result

    def test_each_side_has_all_buttons(self):
        result = parse_secondaries(self._make_secondary_setting())
        for side in [SecondarySide.LEFT, SecondarySide.RIGHT]:
            for button in ChordButton:
                assert button in result[side]

    def test_each_button_has_modulation_variants(self):
        result = parse_secondaries(self._make_secondary_setting())
        button_map = result[SecondarySide.LEFT][ChordButton.SOUTH]
        assert ModulationSide.NONE in button_map
        assert ModulationSide.LEFT in button_map
        assert ModulationSide.RIGHT in button_map

    def test_default_chord_shared_across_buttons(self):
        result = parse_secondaries(self._make_secondary_setting())
        south = result[SecondarySide.LEFT][ChordButton.SOUTH][ModulationSide.NONE]
        west = result[SecondarySide.LEFT][ChordButton.WEST][ModulationSide.NONE]
        # Without button-specific overrides, all buttons share the same DualChord
        assert south is west

    def test_button_override(self):
        setting = self._make_secondary_setting()
        # Add a button-specific override for south
        setting["left"]["south"] = {
            "default": {
                "main": [0, 3, 7],  # Override to minor
            }
        }
        result = parse_secondaries(setting)
        south = result[SecondarySide.LEFT][ChordButton.SOUTH][ModulationSide.NONE]
        west = result[SecondarySide.LEFT][ChordButton.WEST][ModulationSide.NONE]
        # South should be different from west now
        assert south is not west
