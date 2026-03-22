"""Integration tests for PerformFrame check_state().

These tests verify the full dispatch → check_state → widget update flow,
catching the three bug classes introduced by the dirty-flag refactor:

Bug 1: ChordDisplay.chord not initialized (AttributeError on first frame)
Bug 2: Inversion separators not drawn on init (no visual until first dispatch)
Bug 3: pyrsistent types leaking into widget methods when thaw() is removed
"""

from unittest.mock import MagicMock

from display.perform.perform_frame import PerformFrame
from redux import store
from redux.actions import music_engine as me_actions


class TestPerformFrameFirstFrame:
    """Bug 1: check_state() must not crash before any dispatches."""

    def test_check_state_before_any_dispatch(self):
        pf = PerformFrame(container=MagicMock())
        pf._dirty = True
        pf.check_state()  # should not raise

    def test_chord_display_has_chord_attr(self):
        pf = PerformFrame(container=MagicMock())
        assert hasattr(pf.chord_display, "chord")
        assert pf.chord_display.chord == []


class TestPerformFrameWidgetInit:
    """Bug 2: child widgets must be fully initialized after construction."""

    def test_inversion_has_separators(self):
        pf = PerformFrame(container=MagicMock())
        assert len(pf.inversion.separators) > 0

    def test_bass_position_has_separators(self):
        pf = PerformFrame(container=MagicMock())
        assert len(pf.bass_position.separators) > 0


class TestPerformFrameThaw:
    """Bug 3: check_state() must thaw pyrsistent state so downstream
    widget methods receive plain Python types."""

    def test_chord_notes_stored_as_plain_list(self):
        pf = PerformFrame(container=MagicMock())
        store.dispatch(me_actions.play_chord([60, 64, 67]))
        pf._dirty = True
        pf.check_state()
        assert type(pf.state["playingChordNotes"]) is list

    def test_chord_shadow_stored_as_plain_list(self):
        pf = PerformFrame(container=MagicMock())
        store.dispatch(me_actions.change_chord_shadow([60, 64, 67]))
        pf._dirty = True
        pf.check_state()
        assert type(pf.state["shadowChordNotes"]) is list

    def test_scale_stored_as_plain_list(self):
        pf = PerformFrame(container=MagicMock())
        store.dispatch(me_actions.change_scale([0, 2, 4, 5, 7, 9, 11]))
        pf._dirty = True
        pf.check_state()
        assert type(pf.state["scale"]) is list

    def test_chord_type_notes_stored_as_plain_list(self):
        pf = PerformFrame(container=MagicMock())
        store.dispatch(me_actions.change_chord_type({"chord": [0, 4, 7], "root": 0}))
        pf._dirty = True
        pf.check_state()
        assert type(pf.state["chordType"]["notes"]) is list


class TestPerformFrameDirtyFlag:

    def test_dispatch_sets_dirty(self):
        pf = PerformFrame(container=MagicMock())
        pf._dirty = False
        store.dispatch(me_actions.change_key(5))
        assert pf._dirty is True

    def test_check_state_clears_dirty(self):
        pf = PerformFrame(container=MagicMock())
        pf._dirty = True
        pf.check_state()
        assert pf._dirty is False

    def test_check_state_noop_when_not_dirty(self):
        pf = PerformFrame(container=MagicMock())
        # Process any pending state from prior tests
        pf._dirty = True
        pf.check_state()

        original_key = pf.state["key"]
        store.dispatch(me_actions.change_key(7))
        pf._dirty = False  # force not dirty
        pf.check_state()
        assert pf.state["key"] == original_key


class TestPerformFrameChildCheckState:
    """check_state() should cascade to child widgets."""

    def test_spread_check_state_called(self):
        pf = PerformFrame(container=MagicMock())
        store.dispatch(me_actions.change_spread(3))
        pf.check_state()
        assert pf.spread.state["raw_value"] == 3
