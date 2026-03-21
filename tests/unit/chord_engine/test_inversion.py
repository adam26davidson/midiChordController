from unittest.mock import MagicMock

import music_engine.chord_engine.chord_engine_state as state_module
from models.app_parameter import AppParameterType
from music_engine.chord_engine.modules.inversion.chord_inversion import ChordInversion


def make_inversion(**kwargs):
    return ChordInversion(
        kwargs.get("type", AppParameterType.INTERNAL_CHORD_ENGINE),
        kwargs.get("update_chord_engine", MagicMock()),
    )


class TestInversionProcessValue:
    """Test the pure analog-to-discrete conversion with hysteresis snap."""

    def test_center_returns_zero(self):
        inv = make_inversion()
        state_module.state.inversion.range = 4
        state_module.state.inversion.value = 0
        assert inv.process_value(0.0) == 0

    def test_full_positive_returns_max(self):
        inv = make_inversion()
        state_module.state.inversion.range = 4
        state_module.state.inversion.value = 0
        assert inv.process_value(0.999) == 4

    def test_full_negative_returns_min(self):
        inv = make_inversion()
        state_module.state.inversion.range = 4
        state_module.state.inversion.value = 0
        assert inv.process_value(-0.999) == -4

    def test_range_one(self):
        inv = make_inversion()
        state_module.state.inversion.range = 1
        state_module.state.inversion.value = 0
        assert inv.process_value(-0.999) == -1
        assert inv.process_value(0.0) == 0
        assert inv.process_value(0.999) == 1

    def test_snap_prevents_jitter_upward(self):
        inv = make_inversion()
        state_module.state.inversion.range = 4
        state_module.state.inversion.value = 0
        # A value just barely above the threshold for +1 should snap back to 0
        # due to hysteresis
        result = inv.process_value(0.112)
        assert result == 0  # snapped back

    def test_snap_prevents_jitter_downward(self):
        inv = make_inversion()
        state_module.state.inversion.range = 4
        state_module.state.inversion.value = 0
        result = inv.process_value(-0.112)
        assert result == 0

    def test_large_value_breaks_through_snap(self):
        inv = make_inversion()
        state_module.state.inversion.range = 4
        state_module.state.inversion.value = 0
        result = inv.process_value(0.5)
        assert result > 0


class TestInversionSetValue:
    def test_set_value_updates_state(self):
        mock_update = MagicMock()
        inv = make_inversion(update_chord_engine=mock_update)
        state_module.state.inversion.value = 0
        inv.set_value(2)
        assert state_module.state.inversion.value == 2
        mock_update.assert_called()

    def test_set_value_clamps_to_range(self):
        inv = make_inversion()
        state_module.state.inversion.range = 3
        inv.set_value(10)
        assert state_module.state.inversion.value == 3

    def test_set_value_clamps_negative(self):
        inv = make_inversion()
        state_module.state.inversion.range = 3
        inv.set_value(-10)
        assert state_module.state.inversion.value == -3

    def test_set_value_noop_when_locked(self):
        inv = make_inversion()
        state_module.state.inversion.locked = True
        state_module.state.inversion.value = 0
        inv.set_value(2)
        assert state_module.state.inversion.value == 0

    def test_set_value_noop_when_same(self):
        mock_update = MagicMock()
        inv = make_inversion(update_chord_engine=mock_update)
        state_module.state.inversion.value = 2
        mock_update.reset_mock()
        inv.set_value(2)
        mock_update.assert_not_called()


class TestInversionIncrementDecrement:
    def test_increment(self):
        inv = make_inversion()
        state_module.state.inversion.value = 0
        state_module.state.inversion.range = 4
        inv.increment()
        assert state_module.state.inversion.value == 1

    def test_decrement(self):
        inv = make_inversion()
        state_module.state.inversion.value = 0
        state_module.state.inversion.range = 4
        inv.decrement()
        assert state_module.state.inversion.value == -1

    def test_increment_at_max_stays(self):
        inv = make_inversion()
        state_module.state.inversion.value = 4
        state_module.state.inversion.range = 4
        inv.increment()
        assert state_module.state.inversion.value == 4

    def test_decrement_at_min_stays(self):
        inv = make_inversion()
        state_module.state.inversion.value = -4
        state_module.state.inversion.range = 4
        inv.decrement()
        assert state_module.state.inversion.value == -4


class TestInversionSetRange:
    def test_set_range(self):
        inv = make_inversion()
        inv.set_range(6)
        assert state_module.state.inversion.range == 6

    def test_set_range_clamps_max(self):
        inv = make_inversion()
        inv.set_range(100)
        from constants import MAX_INVERSION_RANGE
        assert state_module.state.inversion.range == MAX_INVERSION_RANGE

    def test_set_range_clamps_min(self):
        inv = make_inversion()
        inv.set_range(-5)
        assert state_module.state.inversion.range == 0

    def test_set_range_re_clamps_value(self):
        inv = make_inversion()
        state_module.state.inversion.range = 10
        state_module.state.inversion.value = 8
        inv.set_range(3)
        assert state_module.state.inversion.value == 3

    def test_set_range_re_clamps_negative_value(self):
        inv = make_inversion()
        state_module.state.inversion.range = 10
        state_module.state.inversion.value = -8
        inv.set_range(3)
        assert state_module.state.inversion.value == -3


class TestInversionToggleLock:
    def test_toggle_lock_on(self):
        inv = make_inversion()
        state_module.state.inversion.locked = False
        inv.toggle_lock()
        assert state_module.state.inversion.locked is True

    def test_toggle_lock_off(self):
        inv = make_inversion()
        state_module.state.inversion.locked = True
        inv.toggle_lock()
        assert state_module.state.inversion.locked is False
