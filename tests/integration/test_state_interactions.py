"""Integration tests for state interactions (functional test plan section 19).

Tests combined features and live parameter changes during playback.
"""

from __future__ import annotations

import time

from tests.integration.conftest import PiClient
from tests.integration.helpers import (
    assert_no_stuck_notes,
    note_numbers,
    note_ons,
)


class TestLiveChanges:

    def test_key_transpose_while_playing(self, pi: PiClient) -> None:
        pi.event("SOUTH_BUTTON", "ON")
        time.sleep(0.3)
        before_notes = note_numbers(pi.midi_history(types=["note_on"]))
        before_pc = {n % 12 for n in before_notes}

        pi.clear_midi_history()
        pi.event("RIGHT_STICK_Y_POLAR", "POSITIVE")
        time.sleep(0.3)

        # Should see note_offs for old chord and note_ons for transposed chord
        events = pi.midi_history(types=["note_on", "note_off"])
        new_on = note_ons(events)
        if new_on:
            new_pc = {e["note_number"] % 12 for e in new_on}
            expected_pc = {(n + 1) % 12 for n in before_pc}
            assert new_pc == expected_pc, (
                f"Live transpose: expected {expected_pc}, got {new_pc}"
            )

        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.1)

    def test_octave_shift_while_playing(self, pi: PiClient) -> None:
        pi.event("SOUTH_BUTTON", "ON")
        time.sleep(0.3)

        pi.clear_midi_history()
        pi.event("DPAD_Y", "POSITIVE")
        time.sleep(0.3)

        events = pi.midi_history(types=["note_on", "note_off"])
        on_events = note_ons(events)
        # Verify new notes appeared (chord was re-voiced)
        assert len(on_events) > 0, "Octave shift while playing should re-voice chord"

        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.1)

    def test_inversion_change_during_held_chord(self, pi: PiClient) -> None:
        pi.analog("GYRO_PITCH", 0.0)
        time.sleep(0.1)
        pi.event("SOUTH_BUTTON", "ON")
        time.sleep(0.3)
        before = note_numbers(pi.midi_history(types=["note_on"]))

        pi.clear_midi_history()
        pi.analog("GYRO_PITCH", 0.7)
        time.sleep(0.3)

        events = pi.midi_history(types=["note_on"])
        if events:
            after = note_numbers(events)
            # Pitch classes should be same but octave arrangement different
            before_pc = {n % 12 for n in before}
            after_pc = {n % 12 for n in after}
            assert before_pc == after_pc

        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.1)

    def test_preset_switch_while_playing(self, pi: PiClient) -> None:
        """Switching presets during playback should cleanly stop old notes."""
        pi.event("SOUTH_BUTTON", "ON")
        time.sleep(0.3)

        pi.clear_midi_history()
        pi.load_preset(1)
        time.sleep(0.3)

        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.3)

        # Load preset back to default for other tests
        pi.load_preset(0)
        time.sleep(0.2)

        events = pi.midi_history(count=200, types=["note_on", "note_off"])
        assert_no_stuck_notes(events, "preset switch while playing")


class TestCombinedFeatures:

    def test_hold_plus_modulation(self, pi: PiClient) -> None:
        # Enable hold
        pi.event("RIGHT_OPTION", "ON")
        time.sleep(0.1)
        pi.event("RIGHT_OPTION", "OFF")
        time.sleep(0.1)

        # Play chord (held)
        pi.event("SOUTH_BUTTON", "ON")
        time.sleep(0.2)
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.2)

        # Activate modulation — should replace held chord
        pi.clear_midi_history()
        pi.event("LEFT_BUMPER", "ON")
        time.sleep(0.2)
        pi.event("SOUTH_BUTTON", "ON")
        time.sleep(0.2)
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.2)

        events = pi.midi_history(types=["note_on"])
        assert len(events) > 0, "Modulated chord should play during hold"

        # Cleanup
        pi.event("LEFT_BUMPER", "OFF")
        time.sleep(0.1)
        pi.event("RIGHT_OPTION", "ON")
        time.sleep(0.1)
        pi.event("RIGHT_OPTION", "OFF")
        time.sleep(0.2)

    def test_multiple_features_no_stuck_notes(self, pi: PiClient) -> None:
        """Activate several features and verify clean cleanup."""
        # Key transpose
        pi.event("RIGHT_STICK_Y_POLAR", "POSITIVE")
        time.sleep(0.05)

        # Inversion
        pi.analog("GYRO_PITCH", 0.4)
        time.sleep(0.05)

        # Play chord
        pi.event("SOUTH_BUTTON", "ON")
        time.sleep(0.2)

        # Modulation while playing
        pi.event("LEFT_BUMPER", "ON")
        time.sleep(0.2)
        pi.event("LEFT_BUMPER", "OFF")
        time.sleep(0.1)

        # Bass
        pi.event("LEFT_TRIGGER", "ON")
        time.sleep(0.2)
        pi.event("LEFT_TRIGGER", "OFF")
        time.sleep(0.1)

        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.3)

        events = pi.midi_history(count=500, types=["note_on", "note_off"])
        assert_no_stuck_notes(events, "multiple features combined")
