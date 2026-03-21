"""Tests for ChordDisplay widget initialization and method safety.

Bug 1: ChordDisplay.set_chord_shadow() and play_chord() iterate self.chord,
which was only set when set_chord() was called — not in __init__. With the
dirty-flag refactor, check_state() can invoke these methods on the first frame
before any chord has been dispatched, causing an AttributeError.
"""

from unittest.mock import MagicMock

from display.chord_display import ChordDisplay


class TestChordDisplayInit:

    def test_chord_attribute_exists_after_init(self):
        cd = ChordDisplay(master=MagicMock())
        assert hasattr(cd, "chord")
        assert cd.chord == []

    def test_all_expected_attributes_exist(self):
        cd = ChordDisplay(master=MagicMock())
        for attr in ("scale_notes", "modulation_state", "key", "root",
                      "bass_note", "chord", "notes", "key_text",
                      "chord_name", "bass"):
            assert hasattr(cd, attr), f"missing attribute: {attr}"


class TestChordDisplayBeforeSetChord:
    """Methods that iterate self.chord must be safe before set_chord()."""

    def test_set_chord_shadow_does_not_crash(self):
        cd = ChordDisplay(master=MagicMock())
        cd.set_chord_shadow()  # iterates self.chord — should be a no-op

    def test_play_chord_does_not_crash(self):
        cd = ChordDisplay(master=MagicMock())
        cd.play_chord()  # iterates self.chord — should be a no-op


class TestChordDisplaySetChord:

    def test_set_chord_populates_chord(self):
        cd = ChordDisplay(master=MagicMock())
        cd.set_chord([0, 4, 7], 0)
        assert len(cd.chord) == 3

    def test_set_chord_then_shadow_does_not_crash(self):
        cd = ChordDisplay(master=MagicMock())
        cd.set_chord([0, 4, 7], 0)
        cd.set_chord_shadow()

    def test_set_chord_then_play_does_not_crash(self):
        cd = ChordDisplay(master=MagicMock())
        cd.set_chord([0, 4, 7], 0)
        cd.play_chord()
