"""Test that chord display updates happen in the correct order.

Bug: When switching chords, chordNotes and chordType both change in the same
frame. check_state() processes chordNotes first, calling chord_display.play_chord()
which iterates chord_display.chord — still the OLD chord type. The chordType
update runs afterward. Result: first press of a new chord only shows the bass
note correctly on the chord display; chord notes are wrong until the second press.

Fix: chordType must be updated before chordNotes in check_state(), so
chord_display.chord is current when play_chord() iterates it.
"""

from unittest.mock import MagicMock, call, patch

from redux import store
from redux.actions import music_engine as me_actions

from display.perform.perform_frame import PerformFrame


def _make_perform_frame():
    pf = PerformFrame(container=MagicMock())
    pf._dirty = False
    return pf


def _dispatch_and_check(pf, *actions):
    for action in actions:
        store.dispatch(action)
    pf._dirty = True
    pf.check_state()


class TestChordDisplayOrderingOnChordSwitch:
    """chord_display.set_chord() must run before chord_display.play_chord()
    when both chordType and chordNotes change in the same frame."""

    def test_set_chord_before_play_chord(self):
        """set_chord must be called before play_chord on the chord display
        so that play_chord iterates the correct (new) chord notes."""
        pf = _make_perform_frame()

        # Set up initial chord
        _dispatch_and_check(pf,
            me_actions.change_chord_type({"chord": [0, 4, 7], "root": 0}),
            me_actions.play_chord([60, 64, 67]))

        call_order = []
        original_set_chord = pf.chord_display.set_chord
        original_play_chord = pf.chord_display.play_chord

        def track_set_chord(*args, **kwargs):
            call_order.append("set_chord")
            return original_set_chord(*args, **kwargs)

        def track_play_chord(*args, **kwargs):
            call_order.append("play_chord")
            return original_play_chord(*args, **kwargs)

        with patch.object(pf.chord_display, "set_chord", side_effect=track_set_chord), \
             patch.object(pf.chord_display, "play_chord", side_effect=track_play_chord):
            # Switch to a different chord — both type and notes change
            _dispatch_and_check(pf,
                me_actions.change_chord_type({"chord": [0, 3, 7], "root": 0}),
                me_actions.play_chord([60, 63, 67]))

            assert "set_chord" in call_order, "set_chord was never called"
            assert "play_chord" in call_order, "play_chord was never called"

            set_idx = call_order.index("set_chord")
            play_idx = call_order.index("play_chord")
            assert set_idx < play_idx, (
                f"set_chord must be called before play_chord, "
                f"but call order was: {call_order}"
            )

    def test_chord_display_has_new_chord_when_play_runs(self):
        """When play_chord() runs, chord_display.chord should already
        contain the new chord type notes."""
        pf = _make_perform_frame()

        _dispatch_and_check(pf,
            me_actions.change_chord_type({"chord": [0, 4, 7], "root": 0}),
            me_actions.play_chord([60, 64, 67]))

        chord_at_play_time = None
        original_play = pf.chord_display.play_chord

        def capture_chord_at_play(*args, **kwargs):
            nonlocal chord_at_play_time
            chord_at_play_time = list(pf.chord_display.chord)
            return original_play(*args, **kwargs)

        with patch.object(pf.chord_display, "play_chord", side_effect=capture_chord_at_play):
            _dispatch_and_check(pf,
                me_actions.change_chord_type({"chord": [0, 3, 7], "root": 0}),
                me_actions.play_chord([60, 63, 67]))

            assert chord_at_play_time is not None, "play_chord was never called"
            # The chord display should have the NEW minor chord [0, 3, 7]
            # converted to note classes, not the old major [0, 4, 7]
            assert 4 not in chord_at_play_time, (
                f"chord_display.chord still had old major third (4) when "
                f"play_chord ran: {chord_at_play_time}"
            )
            assert 3 in chord_at_play_time, (
                f"chord_display.chord missing new minor third (3) when "
                f"play_chord ran: {chord_at_play_time}"
            )
