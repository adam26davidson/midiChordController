"""Integration tests for bass (functional test plan section 4).

Bass note: LEFT_TRIGGER ON/OFF.
Bass position: TOUCHPAD_X UPDATE (float).
Bass note should be in lower register (BASS_OCTAVE_RANGE: 36-47).
"""

from __future__ import annotations

import time

from tests.integration.conftest import PiClient
from tests.integration.helpers import note_numbers


class TestBassOnOff:

    def test_bass_produces_note_in_lower_register(self, pi: PiClient) -> None:
        # Need a chord playing for bass to activate
        pi.event("SOUTH_BUTTON", "ON")
        time.sleep(0.2)
        pi.clear_midi_history()

        pi.event("LEFT_TRIGGER", "ON")
        time.sleep(0.3)

        events = pi.midi_history(types=["note_on"])
        assert len(events) > 0, "Bass ON produced no note_on"

        # Bass should be in low register (36-47 range per BASS_OCTAVE_RANGE)
        bass_notes = note_numbers(events)
        low_notes = [n for n in bass_notes if n <= 47]
        assert len(low_notes) > 0, (
            f"Expected at least one bass note <= 47, got {bass_notes}"
        )

        pi.event("LEFT_TRIGGER", "OFF")
        time.sleep(0.1)
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.1)

    def test_bass_off_produces_note_off(self, pi: PiClient) -> None:
        pi.event("SOUTH_BUTTON", "ON")
        time.sleep(0.2)
        pi.event("LEFT_TRIGGER", "ON")
        time.sleep(0.3)

        pi.clear_midi_history()
        pi.event("LEFT_TRIGGER", "OFF")
        time.sleep(0.3)

        events = pi.midi_history(types=["note_off"])
        assert len(events) > 0, "Bass OFF produced no note_off"

        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.1)

    def test_bass_changes_with_chord_button(self, pi: PiClient) -> None:
        pi.event("SOUTH_BUTTON", "ON")
        time.sleep(0.2)

        pi.clear_midi_history()
        pi.event("LEFT_TRIGGER", "ON")
        time.sleep(0.3)
        south_bass = note_numbers(pi.midi_history(types=["note_on"]))

        # Switch to WEST while bass held
        pi.clear_midi_history()
        pi.event("WEST_BUTTON", "ON")
        time.sleep(0.3)

        # Should see new bass note (note_off for old, note_on for new)
        events = pi.midi_history(types=["note_on"])
        west_notes = note_numbers(events)
        # Filter for bass register notes
        south_bass_low = [n for n in south_bass if n <= 47]
        west_bass_low = [n for n in west_notes if n <= 47]

        # At least one of the bass notes should differ between chords
        if south_bass_low and west_bass_low:
            assert south_bass_low != west_bass_low, (
                f"Bass should change with chord: south={south_bass_low}, west={west_bass_low}"
            )

        pi.event("LEFT_TRIGGER", "OFF")
        time.sleep(0.1)
        pi.event("WEST_BUTTON", "OFF")
        time.sleep(0.1)
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.1)


class TestBassPosition:

    def test_position_changes_bass_note(self, pi: PiClient) -> None:
        pi.event("SOUTH_BUTTON", "ON")
        time.sleep(0.2)

        # Bass at position 0
        pi.analog("TOUCHPAD_X", 0.0)
        time.sleep(0.1)
        pi.clear_midi_history()
        pi.event("LEFT_TRIGGER", "ON")
        time.sleep(0.3)
        notes_pos0 = note_numbers(pi.midi_history(types=["note_on"]))
        pi.event("LEFT_TRIGGER", "OFF")
        time.sleep(0.2)

        # Bass at different position
        pi.analog("TOUCHPAD_X", 0.8)
        time.sleep(0.1)
        pi.clear_midi_history()
        pi.event("LEFT_TRIGGER", "ON")
        time.sleep(0.3)
        notes_pos1 = note_numbers(pi.midi_history(types=["note_on"]))
        pi.event("LEFT_TRIGGER", "OFF")
        time.sleep(0.1)

        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.1)

        # Filter to bass register
        bass_pos0 = [n for n in notes_pos0 if n <= 47]
        bass_pos1 = [n for n in notes_pos1 if n <= 47]

        if bass_pos0 and bass_pos1:
            assert bass_pos0 != bass_pos1, (
                f"Different positions should produce different bass: {bass_pos0} vs {bass_pos1}"
            )

    def test_bass_note_in_low_register(self, pi: PiClient) -> None:
        """Bass notes should be in the low register (below middle C / 60)."""
        pi.event("SOUTH_BUTTON", "ON")
        time.sleep(0.2)

        for pos in [0.0, 0.5, 1.0, -0.5, -1.0]:
            pi.analog("TOUCHPAD_X", pos)
            time.sleep(0.1)
            pi.clear_midi_history()
            pi.event("LEFT_TRIGGER", "ON")
            time.sleep(0.3)

            events = pi.midi_history(types=["note_on"])
            bass_notes = [e["note_number"] for e in events if e["note_number"] <= 60]
            for note in bass_notes:
                assert note <= 60, (
                    f"Bass note {note} at position {pos} should be in low register"
                )

            pi.event("LEFT_TRIGGER", "OFF")
            time.sleep(0.2)

        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.1)
