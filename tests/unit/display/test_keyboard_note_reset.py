"""Test that old chord notes are reset on the keyboard when chord notes change.

Bug: When a chord is playing and inversion changes the voicing, __play_chord()
turns on the new notes but never turns off the old ones. Notes that leave the
chord (e.g., higher notes when moving inversion back down) remain visually "on".

The fix should reset old playing notes that are not in the new chord before
calling keyboard.play() with the new notes.
"""

from unittest.mock import MagicMock, patch

from display.perform.perform_frame import PerformFrame
from redux import store
from redux.actions import music_engine as me_actions


class TestChordNoteResetOnChange:
    """When playing chord notes change (e.g., due to inversion), old notes
    that are no longer in the new chord must be reset on the keyboard."""

    def _make_perform_frame(self):
        pf = PerformFrame(container=MagicMock())
        # Clear any init-time dirtiness
        pf._dirty = False
        return pf

    def test_old_notes_reset_when_chord_notes_change(self):
        """Play a chord, then change to different notes. Notes that were in
        the old chord but not in the new one should be reset on the keyboard."""
        pf = self._make_perform_frame()

        # Play initial chord
        store.dispatch(me_actions.play_chord([60, 64, 67]))
        pf._dirty = True
        pf.check_state()
        assert pf.state["playingChordNotes"] == [60, 64, 67]

        # Now inversion changes the chord notes — note 60 is gone, 72 is added
        with patch.object(pf.keyboard, "reset") as mock_reset:
            store.dispatch(me_actions.play_chord([64, 67, 72]))
            pf._dirty = True
            pf.check_state()

            # Note 60 was in the old chord but not the new one — must be reset
            reset_calls = mock_reset.call_args_list
            reset_notes = []
            for c in reset_calls:
                reset_notes.extend(c[0][0])
            assert 60 in reset_notes, (
                f"Note 60 was not reset on keyboard. reset calls: {reset_calls}"
            )

    def test_common_notes_not_reset(self):
        """Notes that remain in both old and new chords should NOT be reset."""
        pf = self._make_perform_frame()

        store.dispatch(me_actions.play_chord([60, 64, 67]))
        pf._dirty = True
        pf.check_state()

        with patch.object(pf.keyboard, "reset") as mock_reset:
            store.dispatch(me_actions.play_chord([64, 67, 72]))
            pf._dirty = True
            pf.check_state()

            reset_notes = []
            for c in mock_reset.call_args_list:
                reset_notes.extend(c[0][0])
            assert 64 not in reset_notes, "Note 64 is in both chords — should not be reset"
            assert 67 not in reset_notes, "Note 67 is in both chords — should not be reset"

    def test_all_old_notes_reset_when_fully_different(self):
        """When the chord changes to entirely different notes, all old notes
        should be reset."""
        pf = self._make_perform_frame()

        store.dispatch(me_actions.play_chord([60, 64, 67]))
        pf._dirty = True
        pf.check_state()

        with patch.object(pf.keyboard, "reset") as mock_reset:
            store.dispatch(me_actions.play_chord([72, 76, 79]))
            pf._dirty = True
            pf.check_state()

            reset_notes = []
            for c in mock_reset.call_args_list:
                reset_notes.extend(c[0][0])
            for note in [60, 64, 67]:
                assert note in reset_notes, (
                    f"Note {note} was not reset. reset calls: {mock_reset.call_args_list}"
                )

    def test_no_play_when_same_notes(self):
        """When the same chord is dispatched again, play should not be called."""
        pf = self._make_perform_frame()

        store.dispatch(me_actions.play_chord([60, 64, 67]))
        pf._dirty = True
        pf.check_state()

        with patch.object(pf.keyboard, "play") as mock_play:
            # Dispatch same notes — check_state should see no diff
            store.dispatch(me_actions.play_chord([60, 64, 67]))
            pf._dirty = True
            pf.check_state()

            mock_play.assert_not_called()
