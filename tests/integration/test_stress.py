"""Integration tests for stress/edge cases (functional test plan sections 23-25).

Rapid input, analog jitter, simultaneous changes, clean reset.
"""

from __future__ import annotations

import time

from tests.integration.conftest import PiClient
from tests.integration.helpers import (
    CHORD_BUTTONS,
    assert_no_stuck_notes,
    assert_notes_in_range,
)


class TestStress:

    def test_rapid_button_spam(self, pi: PiClient) -> None:
        """Rapidly press/release all buttons 5 times each."""
        for _ in range(5):
            for button in CHORD_BUTTONS:
                pi.event(button, "ON")
                time.sleep(0.02)
                pi.event(button, "OFF")
                time.sleep(0.02)

        time.sleep(0.5)
        events = pi.midi_history(count=1000, types=["note_on", "note_off"])
        assert_no_stuck_notes(events, "rapid button spam")

    def test_analog_jitter_during_chord(self, pi: PiClient) -> None:
        """Rapid small GYRO_PITCH changes while chord is held."""
        pi.event("SOUTH_BUTTON", "ON")
        time.sleep(0.2)

        # Simulate gyro jitter
        for i in range(20):
            value = 0.01 * (i % 3)  # Small oscillations near 0
            pi.analog("GYRO_PITCH", value)
            time.sleep(0.02)

        time.sleep(0.2)
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.3)

        events = pi.midi_history(count=500, types=["note_on", "note_off"])
        assert_no_stuck_notes(events, "analog jitter")

    def test_simultaneous_analog_and_button(self, pi: PiClient) -> None:
        """Change multiple analog values while pressing buttons."""
        pi.analog("GYRO_PITCH", 0.3)
        pi.event("SOUTH_BUTTON", "ON")
        time.sleep(0.1)

        pi.analog("GYRO_PITCH", 0.6)
        pi.event("RIGHT_STICK_X_POLAR", "POSITIVE")
        time.sleep(0.1)

        pi.event("WEST_BUTTON", "ON")
        pi.analog("GYRO_PITCH", 0.1)
        time.sleep(0.1)

        pi.event("SOUTH_BUTTON", "OFF")
        pi.event("WEST_BUTTON", "OFF")
        time.sleep(0.3)

        events = pi.midi_history(count=500, types=["note_on", "note_off"])
        assert_no_stuck_notes(events, "simultaneous analog+button")

    def test_all_notes_valid_midi_under_stress(self, pi: PiClient) -> None:
        """Under various parameter extremes, all notes should be valid MIDI (0-127)."""
        # Extreme octave up
        for _ in range(5):
            pi.event("DPAD_Y", "POSITIVE")
            time.sleep(0.02)

        # Extreme spread
        for _ in range(10):
            pi.event("RIGHT_STICK_X_POLAR", "POSITIVE")
            time.sleep(0.02)

        # Max voice count
        for _ in range(10):
            pi.event("LEFT_STICK_X_POLAR", "POSITIVE")
            time.sleep(0.02)

        time.sleep(0.2)

        for button in CHORD_BUTTONS:
            pi.clear_midi_history()
            pi.event(button, "ON")
            time.sleep(0.3)
            events = pi.midi_history(types=["note_on"])
            assert_notes_in_range(events, low=0, high=127, context=f"extreme params + {button}")
            pi.event(button, "OFF")
            time.sleep(0.1)
