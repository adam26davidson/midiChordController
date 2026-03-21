from unittest.mock import MagicMock

import music_engine.chord_engine.chord_engine_state as state_module
from constants import MAX_OCTAVE_SHIFT
from models.app_parameter import AppParameterType
from music_engine.chord_engine.modules.chord_octave import ChordOctave


def make_chord_octave(**kwargs):
    return ChordOctave(
        kwargs.get("type", AppParameterType.INTERNAL_CHORD_ENGINE),
        kwargs.get("update_chord_engine", MagicMock()),
    )


class TestChordOctaveApply:
    def test_apply_no_shift(self):
        co = make_chord_octave()
        state_module.state.chord_octave = 0
        assert co.apply([60, 64, 67]) == [60, 64, 67]

    def test_apply_shift_up_one(self):
        co = make_chord_octave()
        state_module.state.chord_octave = 1
        assert co.apply([60, 64, 67]) == [72, 76, 79]

    def test_apply_shift_down_one(self):
        co = make_chord_octave()
        state_module.state.chord_octave = -1
        assert co.apply([60, 64, 67]) == [48, 52, 55]

    def test_apply_shift_up_two(self):
        co = make_chord_octave()
        state_module.state.chord_octave = 2
        assert co.apply([60]) == [84]

    def test_apply_empty_list(self):
        co = make_chord_octave()
        state_module.state.chord_octave = 1
        assert co.apply([]) == []


class TestChordOctaveSet:
    def test_set_basic(self):
        co = make_chord_octave()
        co.set(2)
        assert state_module.state.chord_octave == 2

    def test_set_clamps_max(self):
        co = make_chord_octave()
        co.set(99)
        assert state_module.state.chord_octave == MAX_OCTAVE_SHIFT

    def test_set_clamps_min(self):
        co = make_chord_octave()
        co.set(-99)
        assert state_module.state.chord_octave == -MAX_OCTAVE_SHIFT

    def test_set_calls_update(self):
        mock = MagicMock()
        co = make_chord_octave(update_chord_engine=mock)
        mock.reset_mock()
        co.set(1)
        mock.assert_called_once()


class TestChordOctaveIncrementDecrement:
    def test_increment(self):
        co = make_chord_octave()
        state_module.state.chord_octave = 0
        co.increment()
        assert state_module.state.chord_octave == 1

    def test_decrement(self):
        co = make_chord_octave()
        state_module.state.chord_octave = 0
        co.decrement()
        assert state_module.state.chord_octave == -1

    def test_increment_at_max(self):
        co = make_chord_octave()
        state_module.state.chord_octave = MAX_OCTAVE_SHIFT
        co.increment()
        assert state_module.state.chord_octave == MAX_OCTAVE_SHIFT

    def test_decrement_at_min(self):
        co = make_chord_octave()
        state_module.state.chord_octave = -MAX_OCTAVE_SHIFT
        co.decrement()
        assert state_module.state.chord_octave == -MAX_OCTAVE_SHIFT
