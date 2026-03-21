from unittest.mock import MagicMock

import pytest

import music_engine.chord_engine.chord_engine_state as state_module
from music_engine.chord_engine.internal_chord_engine.modules.modulations import Modulations
from music_engine.chord_engine.internal_chord_engine.modules.modulations.modulation import Modulation
from music_engine.chord_engine.state.modulations_state import ModulationSide

C_MAJOR = [0, 2, 4, 5, 7, 9, 11]

CUSTOM_SETTING = {"type": "custom", "map": [0, 10, 8, 7, 5, 3, 1]}
MODAL_SETTING = {"type": "modal", "map": [0, 5]}

DEFAULT_PRESET_MODULATIONS = {"left": MODAL_SETTING, "right": CUSTOM_SETTING}


# ---------------------------------------------------------------------------
# Modulation pure logic
# ---------------------------------------------------------------------------


class TestModulationCustom:
    """Custom modulation with an explicit note map."""

    @pytest.fixture
    def mod(self):
        return Modulation(C_MAJOR, CUSTOM_SETTING)

    def test_map_is_setting_map(self, mod):
        assert mod.map == [0, 10, 8, 7, 5, 3, 1]

    def test_offsets(self, mod):
        # offsets[i] = map[i] - scale[i]
        expected = [
            0 - 0,   # 0
            10 - 2,   # 8
            8 - 4,    # 4
            7 - 5,    # 2
            5 - 7,    # -2
            3 - 9,    # -6
            1 - 11,   # -10
        ]
        assert mod.offsets == expected

    def test_apply_to_scale(self, mod):
        result = mod.apply_to_scale()
        expected = [(s + o) % 12 for s, o in zip(C_MAJOR, mod.offsets)]
        assert result == expected

    def test_apply_notes(self, mod):
        # Notes 0, 4, 7 have scale indices 0, 2, 4 -> offsets 0, 4, -2
        result = mod.apply([0, 4, 7], C_MAJOR)
        assert result == [0 + 0, 4 + 4, 7 + (-2)]

    def test_apply_one_midi_note(self, mod):
        # MIDI note 60 -> note class 0 -> scale index 0 -> offset 0
        assert mod.apply_one(60, C_MAJOR) == 60


class TestModulationModal:
    """Modal modulation from C major via map [0, 5].

    The algorithm rotates the chromatic scale pattern by
    ((scale[0] - scale[5]) + 12) % 12 = ((0 - 9) + 12) % 12 = 3 semitones,
    producing the modal map [1, 2, 4, 6, 8, 9, 11].
    """

    MODAL_MAP = [1, 2, 4, 6, 8, 9, 11]

    @pytest.fixture
    def mod(self):
        return Modulation(C_MAJOR, MODAL_SETTING)

    def test_find_modal_map(self, mod):
        assert mod.map == self.MODAL_MAP

    def test_offsets(self, mod):
        expected = [m - s for m, s in zip(self.MODAL_MAP, C_MAJOR)]
        assert mod.offsets == expected

    def test_apply_to_scale(self, mod):
        expected = [(s + o) % 12 for s, o in zip(C_MAJOR, mod.offsets)]
        assert mod.apply_to_scale() == expected

    def test_apply_notes(self, mod):
        # Note 5 (F) is scale index 3 -> offset 6-5 = 1 -> becomes 6
        # Note 0 (C) is scale index 0 -> offset 1-0 = 1 -> becomes 1
        # Note 7 (G) is scale index 4 -> offset 8-7 = 1 -> becomes 8
        result = mod.apply([0, 5, 7], C_MAJOR)
        assert result == [1, 6, 8]

    def test_apply_one_midi_note(self, mod):
        # MIDI note 60 -> class 0 -> index 0 -> offset 1 -> 61
        assert mod.apply_one(60, C_MAJOR) == 61
        # MIDI note 65 (F4) -> class 5 -> index 3 -> offset 1 -> 66
        assert mod.apply_one(65, C_MAJOR) == 66


# ---------------------------------------------------------------------------
# Modulations container (uses state and store)
# ---------------------------------------------------------------------------


class TestModulations:

    @pytest.fixture
    def setup(self):
        """Set up state and create a Modulations instance."""
        state = state_module.state
        state.scale.key_agnostic = C_MAJOR
        state.modulation.side = ModulationSide.NONE

        callback = MagicMock()
        modulations = Modulations(DEFAULT_PRESET_MODULATIONS, callback)
        return modulations, callback, state

    def test_apply_returns_notes_unchanged_when_none(self, setup):
        modulations, _, state = setup
        state.modulation.side = ModulationSide.NONE
        notes = [0, 4, 7]
        assert modulations.apply(notes, C_MAJOR) == notes

    def test_apply_uses_left_modulation(self, setup):
        modulations, _, state = setup
        state.modulation.side = ModulationSide.LEFT
        # Left is modal: offsets are all +1 for degrees 0,3,4
        result = modulations.apply([0, 5, 7], C_MAJOR)
        assert result == [1, 6, 8]

    def test_apply_uses_right_modulation(self, setup):
        modulations, _, state = setup
        state.modulation.side = ModulationSide.RIGHT
        # Right is custom: note 0 offset 0, note 4 offset 4, note 7 offset -2
        result = modulations.apply([0, 4, 7], C_MAJOR)
        assert result == [0, 8, 5]

    def test_apply_one_returns_note_unchanged_when_none(self, setup):
        modulations, _, state = setup
        state.modulation.side = ModulationSide.NONE
        assert modulations.apply_one(60, C_MAJOR) == 60

    def test_apply_one_uses_left_modulation(self, setup):
        modulations, _, state = setup
        state.modulation.side = ModulationSide.LEFT
        # MIDI 65 (F) -> Lydian offset +1 -> 66
        assert modulations.apply_one(65, C_MAJOR) == 66

    def test_set_changes_state_and_calls_callback(self, setup):
        modulations, callback, state = setup
        modulations.set(ModulationSide.LEFT)

        assert state.modulation.side == ModulationSide.LEFT
        callback.assert_called_once()

    def test_set_to_same_side_is_noop(self, setup):
        modulations, callback, state = setup
        state.modulation.side = ModulationSide.LEFT

        modulations.set(ModulationSide.LEFT)
        callback.assert_not_called()

    def test_set_back_to_none(self, setup):
        modulations, callback, state = setup
        # First set to LEFT
        modulations.set(ModulationSide.LEFT)
        callback.reset_mock()

        # Then set back to NONE
        modulations.set(ModulationSide.NONE)
        assert state.modulation.side == ModulationSide.NONE
        callback.assert_called_once()
