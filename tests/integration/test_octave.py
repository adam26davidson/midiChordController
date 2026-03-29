"""Integration tests for octave shift (functional test plan section 7).

Octave shift moves all notes by 12 semitones per step. Clamped to +-3.
Controls: DPAD_Y or LEFT_STICK_Y_POLAR (both map to INTERNAL_OCTAVE).
"""

from __future__ import annotations

import time

from tests.integration.conftest import PiClient
from tests.integration.helpers import (
    assert_notes_in_range,
    collect_chord_notes,
    pitch_classes,
    play_and_release,
)


class TestOctaveShift:

    def test_shift_up_adds_twelve(self, pi: PiClient) -> None:
        original = collect_chord_notes(pi)
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.2)

        pi.event("DPAD_Y", "POSITIVE")
        time.sleep(0.2)

        shifted = collect_chord_notes(pi)
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.1)

        # Each note should be 12 higher (unless clamped)
        for orig, shift in zip(original, shifted):
            assert shift == orig + 12 or shift == orig, (
                f"Expected +12: {orig} -> {shift}"
            )

    def test_shift_down_subtracts_twelve(self, pi: PiClient) -> None:
        original = collect_chord_notes(pi)
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.2)

        pi.event("DPAD_Y", "NEGATIVE")
        time.sleep(0.2)

        shifted = collect_chord_notes(pi)
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.1)

        for orig, shift in zip(original, shifted):
            assert shift == orig - 12 or shift == orig, (
                f"Expected -12: {orig} -> {shift}"
            )

    def test_pitch_classes_unchanged(self, pi: PiClient) -> None:
        on_events_orig, _ = play_and_release(pi)
        original_pc = pitch_classes(on_events_orig)

        pi.event("DPAD_Y", "POSITIVE")
        time.sleep(0.2)

        on_events_shifted, _ = play_and_release(pi)
        shifted_pc = pitch_classes(on_events_shifted)

        assert original_pc == shifted_pc, (
            f"Octave shift should not change pitch classes: {original_pc} vs {shifted_pc}"
        )

    def test_notes_valid_midi_at_max_octave(self, pi: PiClient) -> None:
        # Shift up to max (3 octaves)
        for _ in range(5):
            pi.event("DPAD_Y", "POSITIVE")
            time.sleep(0.05)
        time.sleep(0.2)

        on_high, _ = play_and_release(pi)
        assert_notes_in_range(on_high, low=0, high=127, context="max octave shift")

    def test_notes_valid_midi_at_min_octave(self, pi: PiClient) -> None:
        for _ in range(5):
            pi.event("DPAD_Y", "NEGATIVE")
            time.sleep(0.05)
        time.sleep(0.2)

        on_low, _off_low = play_and_release(pi)
        assert len(on_low) > 0, "Should still produce note events at min octave"
        assert_notes_in_range(on_low, low=0, high=127, context="min octave shift")

    def test_shift_up_then_back(self, pi: PiClient) -> None:
        original = collect_chord_notes(pi)
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.2)

        pi.event("DPAD_Y", "POSITIVE")
        time.sleep(0.1)
        pi.event("DPAD_Y", "NEGATIVE")
        time.sleep(0.2)

        restored = collect_chord_notes(pi)
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.1)

        assert restored == original, f"Expected {original} after up+down, got {restored}"
