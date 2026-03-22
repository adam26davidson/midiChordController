"""Tests for modulation display ordering and visual state.

Bug 1 (played notes turning off): When a modulation triggers scale + chordNotes
changes in the same frame, set_scale() was resetting all chord display notes to
dim state AFTER play_chord() had highlighted them as played. Fix: scale context
must resolve before playing state.

Bug 2 (notes not gliding): set_scale() was jumping notes to final positions
before set_modulation() could start the animation. set_modulation() handles its
own set_scale() internally, so the standalone set_scale() call must be skipped
when a modulation is happening.
"""

from unittest.mock import MagicMock, patch

from display.perform.perform_frame import PerformFrame
from redux import store
from redux.actions import music_engine as me_actions


def _make_perform_frame():
    pf = PerformFrame(container=MagicMock())
    pf._dirty = False
    return pf


def _dispatch_and_check(pf, *actions):
    for action in actions:
        store.dispatch(action)
    pf._dirty = True
    pf.check_state()


class TestScaleChangeDoesNotWipePlaying:
    """Bug 1: set_scale must not run after play_chord in the same frame."""

    def test_played_notes_visible_after_scale_and_chord_change(self):
        """When scale and chord notes change together, play_chord must run
        AFTER set_scale so played notes aren't reset to dim state."""
        pf = _make_perform_frame()

        # Initial state: playing a chord in one scale
        _dispatch_and_check(pf,
            me_actions.change_scale([0, 2, 4, 5, 7, 9, 11]),
            me_actions.change_chord_type({"chord": [0, 4, 7], "root": 0}),
            me_actions.play_chord([60, 64, 67]))

        call_order = []
        original_set_scale = pf.chord_display.set_scale
        original_play_chord = pf.chord_display.play_chord

        def track_set_scale(*args, **kwargs):
            call_order.append("set_scale")
            return original_set_scale(*args, **kwargs)

        def track_play_chord(*args, **kwargs):
            call_order.append("play_chord")
            return original_play_chord(*args, **kwargs)

        with patch.object(pf.chord_display, "set_scale", side_effect=track_set_scale), \
             patch.object(pf.chord_display, "play_chord", side_effect=track_play_chord):
            # Modulation changes scale and chord notes in same frame
            _dispatch_and_check(pf,
                me_actions.change_scale([0, 2, 4, 6, 7, 9, 11]),
                me_actions.change_chord_type({"chord": [0, 4, 7], "root": 0}),
                me_actions.play_chord([60, 64, 67, 72]))

            if "set_scale" in call_order and "play_chord" in call_order:
                scale_idx = call_order.index("set_scale")
                play_idx = call_order.index("play_chord")
                assert scale_idx < play_idx, (
                    f"set_scale must run before play_chord, "
                    f"but call order was: {call_order}"
                )

    def test_scale_change_without_chord_change_still_works(self):
        """When only scale changes (no chord notes change), set_scale should
        still run normally."""
        pf = _make_perform_frame()

        _dispatch_and_check(pf, me_actions.change_scale([0, 2, 4, 5, 7, 9, 11]))

        with patch.object(pf.chord_display, "set_scale") as mock_set_scale:
            _dispatch_and_check(pf, me_actions.change_scale([0, 2, 4, 6, 7, 9, 11]))
            mock_set_scale.assert_called_once()


class TestModulationAnimationOrdering:
    """Bug 2: set_modulation must run before standalone set_scale, and
    set_scale must be skipped when modulation handles it."""

    def test_modulation_runs_before_chord_notes(self):
        """set_modulation must run before play_chord so the animation
        starts with notes at their old positions."""
        pf = _make_perform_frame()

        _dispatch_and_check(pf,
            me_actions.change_scale([0, 2, 4, 5, 7, 9, 11]),
            me_actions.change_chord_type({"chord": [0, 4, 7], "root": 0}),
            me_actions.play_chord([60, 64, 67]))

        call_order = []
        original_set_mod = pf.chord_display.set_modulation
        original_play = pf.chord_display.play_chord

        def track_set_mod(*args, **kwargs):
            call_order.append("set_modulation")
            return original_set_mod(*args, **kwargs)

        def track_play(*args, **kwargs):
            call_order.append("play_chord")
            return original_play(*args, **kwargs)

        with patch.object(pf.chord_display, "set_modulation", side_effect=track_set_mod), \
             patch.object(pf.chord_display, "play_chord", side_effect=track_play):
            _dispatch_and_check(pf,
                me_actions.change_modulation(
                    {"side": "left", "scale": [0, 2, 4, 6, 7, 9, 11]}),
                me_actions.change_scale([0, 2, 4, 6, 7, 9, 11]),
                me_actions.play_chord([60, 64, 67, 72]))

            assert "set_modulation" in call_order, "set_modulation was never called"
            if "play_chord" in call_order:
                mod_idx = call_order.index("set_modulation")
                play_idx = call_order.index("play_chord")
                assert mod_idx < play_idx, (
                    f"set_modulation must run before play_chord, "
                    f"but call order was: {call_order}"
                )

    def test_scale_local_state_updated_during_modulation(self):
        """Even when standalone set_scale is skipped, the local scale state
        must still be updated so future diffs work correctly."""
        pf = _make_perform_frame()

        _dispatch_and_check(pf, me_actions.change_scale([0, 2, 4, 5, 7, 9, 11]))

        _dispatch_and_check(pf,
            me_actions.change_modulation(
                {"side": "left", "scale": [0, 2, 4, 6, 7, 9, 11]}),
            me_actions.change_scale([0, 2, 4, 6, 7, 9, 11]))

        assert pf.state["scale"] == [0, 2, 4, 6, 7, 9, 11]

    def test_modulation_back_to_none_allows_set_scale(self):
        """When modulation returns to 'none', standalone set_scale should
        run normally again."""
        pf = _make_perform_frame()

        # Start modulation
        _dispatch_and_check(pf,
            me_actions.change_scale([0, 2, 4, 5, 7, 9, 11]),
            me_actions.change_modulation(
                {"side": "left", "scale": [0, 2, 4, 6, 7, 9, 11]}))

        # End modulation
        _dispatch_and_check(pf,
            me_actions.change_modulation({"side": "none", "scale": []}))

        # Now a plain scale change should call set_scale normally
        with patch.object(pf.chord_display, "set_scale") as mock_set_scale:
            _dispatch_and_check(pf,
                me_actions.change_scale([0, 2, 3, 5, 7, 8, 10]))
            mock_set_scale.assert_called_once()
