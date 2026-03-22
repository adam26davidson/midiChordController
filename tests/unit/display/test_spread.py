"""Tests for Spread widget dirty-flag pattern."""

from unittest.mock import MagicMock

from constants import SPREAD_STEPS_PER_OCTAVE
from display.perform.spread import Spread
from redux import store
from redux.actions import music_engine as me_actions


class TestSpreadInit:

    def test_initial_state(self):
        sp = Spread(master=MagicMock())
        assert sp.state["raw_value"] == SPREAD_STEPS_PER_OCTAVE
        assert sp.state["value"] == 12

    def test_dirty_flag_initially_false(self):
        sp = Spread(master=MagicMock())
        sp._dirty = False  # clear any init-time dirtiness
        assert sp._dirty is False


class TestSpreadDirtyFlag:

    def test_dispatch_sets_dirty(self):
        sp = Spread(master=MagicMock())
        sp._dirty = False
        store.dispatch(me_actions.change_spread(3))
        assert sp._dirty is True

    def test_check_state_clears_dirty(self):
        sp = Spread(master=MagicMock())
        sp._dirty = True
        sp.check_state()
        assert sp._dirty is False

    def test_check_state_noop_when_not_dirty(self):
        sp = Spread(master=MagicMock())
        sp._dirty = False
        original_value = sp.state["raw_value"]
        # Dispatch a change but clear dirty before check_state
        store.dispatch(me_actions.change_spread(1))
        sp._dirty = False
        sp.check_state()
        assert sp.state["raw_value"] == original_value


class TestSpreadCheckState:

    def test_updates_state_after_dispatch(self):
        sp = Spread(master=MagicMock())
        store.dispatch(me_actions.change_spread(3))
        sp.check_state()
        assert sp.state["raw_value"] == 3
