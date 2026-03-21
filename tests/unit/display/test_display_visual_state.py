"""Tests for display visual state consistency.

Verifies that old visual state is properly cleaned up when display values
change, preventing notes or indicators from getting "stuck on".
"""

from unittest.mock import MagicMock, patch

from redux import store
from redux.actions import music_engine as me_actions

from display.perform.perform_frame import PerformFrame


def _make_perform_frame():
    pf = PerformFrame(container=MagicMock())
    pf._dirty = False
    return pf


def _dispatch_and_check(pf, action):
    store.dispatch(action)
    pf._dirty = True
    pf.check_state()


class TestBassNoteResetOnChange:
    """When the playing bass note changes, the old bass note should be
    reset on the keyboard."""

    def test_old_bass_note_reset_when_bass_changes(self):
        pf = _make_perform_frame()

        _dispatch_and_check(pf, me_actions.play_bass(48))
        assert pf.state["playingBassNote"] == 48

        with patch.object(pf.keyboard, "reset") as mock_reset:
            _dispatch_and_check(pf, me_actions.play_bass(52))

            reset_notes = []
            for c in mock_reset.call_args_list:
                reset_notes.extend(c[0][0])
            assert 48 in reset_notes, (
                f"Old bass note 48 was not reset. reset calls: {mock_reset.call_args_list}"
            )

    def test_old_bass_not_reset_if_in_playing_chord(self):
        """If the old bass note is also in the playing chord, it should NOT
        be reset (it's still visually active as a chord note)."""
        pf = _make_perform_frame()

        _dispatch_and_check(pf, me_actions.play_chord([48, 52, 55]))
        _dispatch_and_check(pf, me_actions.play_bass(48))

        with patch.object(pf.keyboard, "reset") as mock_reset:
            _dispatch_and_check(pf, me_actions.play_bass(52))

            reset_notes = []
            for c in mock_reset.call_args_list:
                reset_notes.extend(c[0][0])
            assert 48 not in reset_notes, (
                "Bass note 48 is in the playing chord — should not be reset"
            )


class TestChordTypeChangeWhilePlaying:
    """When the chord type definition changes while notes are playing,
    the playing notes should be re-highlighted after the chord definition
    updates on the keyboard."""

    def test_playing_notes_restored_after_chord_type_change(self):
        pf = _make_perform_frame()

        # Ensure a known initial chord type so the change is always a diff
        _dispatch_and_check(pf, me_actions.change_chord_type(
            {"chord": [0, 4, 7], "root": 0}))
        _dispatch_and_check(pf, me_actions.play_chord([60, 64, 67]))

        with patch.object(pf.keyboard, "play") as mock_play:
            # Chord type changes (e.g., major → minor) — keyboard.set_chord()
            # calls clear_all() which resets all keys. Playing notes should
            # be re-highlighted.
            _dispatch_and_check(pf, me_actions.change_chord_type(
                {"chord": [0, 3, 7], "root": 0}))

            # keyboard.play should have been called to restore playing state
            if mock_play.call_args_list:
                played_notes = mock_play.call_args_list[-1][0][0]
                assert played_notes == [60, 64, 67], (
                    f"Expected playing notes to be restored, got: {played_notes}"
                )
            else:
                raise AssertionError(
                    "keyboard.play() was never called — playing notes lost their visual state"
                )


class TestChordShadowTransitions:
    """Shadow notes should be properly cleaned up during transitions."""

    def test_shadow_reset_when_new_shadow_arrives(self):
        """When shadow chord changes, old shadow notes should be reset."""
        pf = _make_perform_frame()

        _dispatch_and_check(pf, me_actions.change_chord_shadow([60, 64, 67]))
        assert pf.state["shadowChordNotes"] == [60, 64, 67]

        with patch.object(pf.keyboard, "reset") as mock_reset:
            _dispatch_and_check(pf, me_actions.change_chord_shadow([62, 65, 69]))

            reset_notes = []
            for c in mock_reset.call_args_list:
                reset_notes.extend(c[0][0])
            for note in [60, 64, 67]:
                assert note in reset_notes, (
                    f"Old shadow note {note} was not reset"
                )

    def test_new_shadow_notes_set(self):
        """New shadow notes should be set on the keyboard."""
        pf = _make_perform_frame()

        _dispatch_and_check(pf, me_actions.change_chord_shadow([60, 64, 67]))

        with patch.object(pf.keyboard, "set_shadow") as mock_shadow:
            _dispatch_and_check(pf, me_actions.change_chord_shadow([62, 65, 69]))

            mock_shadow.assert_called_with([62, 65, 69])


class TestBassShadowTransitions:

    def test_bass_shadow_reset_when_new_shadow_arrives(self):
        """Old bass shadow should be reset when a new bass shadow arrives."""
        pf = _make_perform_frame()

        _dispatch_and_check(pf, me_actions.change_bass_shadow(48))
        assert pf.state["shadowBassNote"] == 48

        with patch.object(pf.keyboard, "reset") as mock_reset:
            _dispatch_and_check(pf, me_actions.change_bass_shadow(52))

            reset_notes = []
            for c in mock_reset.call_args_list:
                reset_notes.extend(c[0][0])
            assert 48 in reset_notes, (
                f"Old bass shadow note 48 was not reset. calls: {mock_reset.call_args_list}"
            )

    def test_bass_shadow_not_reset_if_in_playing_chord(self):
        """If old bass shadow note is in the playing chord, don't reset it."""
        pf = _make_perform_frame()

        _dispatch_and_check(pf, me_actions.play_chord([48, 52, 55]))
        _dispatch_and_check(pf, me_actions.change_bass_shadow(48))

        with patch.object(pf.keyboard, "reset") as mock_reset:
            _dispatch_and_check(pf, me_actions.change_bass_shadow(52))

            reset_notes = []
            for c in mock_reset.call_args_list:
                reset_notes.extend(c[0][0])
            assert 48 not in reset_notes, (
                "Bass shadow 48 is in the playing chord — should not be reset"
            )


class TestPlayThenStopTransitions:
    """Verify clean transitions between playing and stopped states."""

    def test_stop_chord_transitions_to_shadow(self):
        """When chord stops, notes should transition to shadow state."""
        pf = _make_perform_frame()

        _dispatch_and_check(pf, me_actions.play_chord([60, 64, 67]))

        with patch.object(pf.keyboard, "set_shadow") as mock_shadow:
            _dispatch_and_check(pf, me_actions.stop_chord())

            mock_shadow.assert_called_once_with([60, 64, 67])
            assert pf.state["playingChordNotes"] == []

    def test_stop_bass_transitions_to_shadow(self):
        """When bass stops, note should transition to shadow state."""
        pf = _make_perform_frame()

        _dispatch_and_check(pf, me_actions.play_bass(48))

        with patch.object(pf.keyboard, "set_shadow") as mock_shadow:
            _dispatch_and_check(pf, me_actions.stop_bass())

            # set_shadow should be called with the old bass note
            shadow_notes = []
            for c in mock_shadow.call_args_list:
                shadow_notes.extend(c[0][0])
            assert 48 in shadow_notes
            assert pf.state["playingBassNote"] is None

    def test_play_new_chord_after_stop(self):
        """Playing a new chord after stopping should work cleanly."""
        pf = _make_perform_frame()

        _dispatch_and_check(pf, me_actions.play_chord([60, 64, 67]))
        _dispatch_and_check(pf, me_actions.stop_chord())

        with patch.object(pf.keyboard, "play") as mock_play:
            _dispatch_and_check(pf, me_actions.play_chord([62, 65, 69]))
            mock_play.assert_called_once_with([62, 65, 69])
