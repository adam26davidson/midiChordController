"""Integration tests for hold mode (functional test plan section 8).

Hold mode: RIGHT_OPTION toggles. When active, notes sustain after button release.
"""

from __future__ import annotations

import time

from tests.integration.conftest import PiClient
from tests.integration.helpers import (
    assert_no_stuck_notes,
    note_numbers,
    note_offs,
    note_ons,
)


class TestHold:

    def test_hold_sustains_after_release(self, pi: PiClient) -> None:
        # Enable hold
        pi.event("RIGHT_OPTION", "ON")
        time.sleep(0.1)
        pi.event("RIGHT_OPTION", "OFF")
        time.sleep(0.2)

        # Press and release chord
        pi.event("SOUTH_BUTTON", "ON")
        time.sleep(0.3)
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.3)

        # Should have note_on but NO note_off (notes sustained)
        events = pi.midi_history(types=["note_on", "note_off"])
        on_events = note_ons(events)
        off_events = note_offs(events)
        assert len(on_events) > 0, "No note_on events"
        assert len(off_events) == 0, (
            f"Hold should prevent note_off, but got {len(off_events)} note_offs"
        )

        # Cleanup: disable hold to release notes
        pi.event("RIGHT_OPTION", "ON")
        time.sleep(0.1)
        pi.event("RIGHT_OPTION", "OFF")
        time.sleep(0.2)

    def test_new_chord_replaces_held(self, pi: PiClient) -> None:
        # Enable hold
        pi.event("RIGHT_OPTION", "ON")
        time.sleep(0.1)
        pi.event("RIGHT_OPTION", "OFF")
        time.sleep(0.2)

        # Play SOUTH, release (held)
        pi.event("SOUTH_BUTTON", "ON")
        time.sleep(0.3)
        south_notes = sorted(note_numbers(pi.midi_history(types=["note_on"])))
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.2)

        # Play WEST (should replace held SOUTH)
        pi.clear_midi_history()
        pi.event("WEST_BUTTON", "ON")
        time.sleep(0.3)

        events = pi.midi_history(types=["note_on", "note_off"])
        # Should see note_offs for SOUTH and note_ons for WEST
        offs = sorted(note_numbers(note_offs(events)))
        assert offs == south_notes, (
            f"Expected SOUTH note_offs {south_notes}, got {offs}"
        )

        pi.event("WEST_BUTTON", "OFF")
        time.sleep(0.1)

        # Cleanup
        pi.event("RIGHT_OPTION", "ON")
        time.sleep(0.1)
        pi.event("RIGHT_OPTION", "OFF")
        time.sleep(0.2)

    def test_hold_off_releases_all(self, pi: PiClient) -> None:
        # Enable hold
        pi.event("RIGHT_OPTION", "ON")
        time.sleep(0.1)
        pi.event("RIGHT_OPTION", "OFF")
        time.sleep(0.2)

        # Play and release chord (notes held)
        pi.event("SOUTH_BUTTON", "ON")
        time.sleep(0.3)
        held_notes = sorted(note_numbers(pi.midi_history(types=["note_on"])))
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.2)

        # Disable hold — should release all held notes
        pi.clear_midi_history()
        pi.event("RIGHT_OPTION", "ON")
        time.sleep(0.1)
        pi.event("RIGHT_OPTION", "OFF")
        time.sleep(0.3)

        events = pi.midi_history(types=["note_off"])
        released = sorted(note_numbers(events))
        assert released == held_notes, (
            f"Hold off should release {held_notes}, got {released}"
        )

    def test_no_stuck_notes_after_hold_cycle(self, pi: PiClient) -> None:
        """Full hold cycle: enable, play, release button, disable hold."""
        # Enable hold
        pi.event("RIGHT_OPTION", "ON")
        time.sleep(0.1)
        pi.event("RIGHT_OPTION", "OFF")
        time.sleep(0.1)

        pi.event("SOUTH_BUTTON", "ON")
        time.sleep(0.2)
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.2)
        pi.event("WEST_BUTTON", "ON")
        time.sleep(0.2)
        pi.event("WEST_BUTTON", "OFF")
        time.sleep(0.2)

        # Disable hold
        pi.event("RIGHT_OPTION", "ON")
        time.sleep(0.1)
        pi.event("RIGHT_OPTION", "OFF")
        time.sleep(0.3)

        events = pi.midi_history(count=200, types=["note_on", "note_off"])
        assert_no_stuck_notes(events, "hold cycle")
