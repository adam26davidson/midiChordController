from unittest.mock import MagicMock

import music_engine.chord_engine.chord_engine_state as state_module
from constants import MAX_SPREAD_OCTAVES, SPREAD_STEPS_PER_OCTAVE
from models.app_parameter import AppParameterType
from music_engine.chord_engine.modules.spread import Spread


def make_spread(**kwargs):
    return Spread(
        kwargs.get("type", AppParameterType.INTERNAL_CHORD_ENGINE),
        kwargs.get("update_chord_engine", MagicMock()),
    )


class TestSpreadSet:
    def test_set_basic(self):
        spread = make_spread()
        spread.set(10)
        assert state_module.state.spread == 10

    def test_set_clamps_max(self):
        spread = make_spread()
        max_val = SPREAD_STEPS_PER_OCTAVE * MAX_SPREAD_OCTAVES - 1
        spread.set(999)
        assert state_module.state.spread == max_val

    def test_set_clamps_min(self):
        spread = make_spread()
        spread.set(-5)
        assert state_module.state.spread == 0

    def test_set_calls_update(self):
        mock = MagicMock()
        spread = make_spread(update_chord_engine=mock)
        mock.reset_mock()
        spread.set(10)
        mock.assert_called_once()


class TestSpreadIncrementDecrement:
    def test_increment(self):
        spread = make_spread()
        state_module.state.spread = 5
        spread.increment()
        assert state_module.state.spread == 6

    def test_decrement(self):
        spread = make_spread()
        state_module.state.spread = 5
        spread.decrement()
        assert state_module.state.spread == 4

    def test_decrement_at_zero(self):
        spread = make_spread()
        state_module.state.spread = 0
        spread.decrement()
        assert state_module.state.spread == 0
