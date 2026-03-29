"""Integration tests for key/transpose (functional test plan section 2).

Key changes shift all pitch classes by semitones. Control: RIGHT_STICK_Y_POLAR.
"""

from __future__ import annotations

import time

from tests.integration.conftest import PiClient
from tests.integration.helpers import (
    CHORD_BUTTONS,
    collect_chord_notes,
    play_and_release,
)


class TestKeyTranspose:

    def test_transpose_up_shifts_pitch_classes(self, pi: PiClient) -> None:
        original = collect_chord_notes(pi)
        original_classes = {n % 12 for n in original}
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.2)

        pi.event("RIGHT_STICK_Y_POLAR", "POSITIVE")
        time.sleep(0.2)

        transposed = collect_chord_notes(pi)
        transposed_classes = {n % 12 for n in transposed}
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.1)

        expected = {(n + 1) % 12 for n in original_classes}
        assert transposed_classes == expected, (
            f"Expected {expected} after +1 semitone, got {transposed_classes}"
        )

    def test_transpose_down_shifts_back(self, pi: PiClient) -> None:
        original = collect_chord_notes(pi)
        original_classes = {n % 12 for n in original}
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.2)

        # Up then down should return to original
        pi.event("RIGHT_STICK_Y_POLAR", "POSITIVE")
        time.sleep(0.1)
        pi.event("RIGHT_STICK_Y_POLAR", "NEGATIVE")
        time.sleep(0.2)

        restored = collect_chord_notes(pi)
        restored_classes = {n % 12 for n in restored}
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.1)

        assert restored_classes == original_classes

    def test_twelve_increments_wraps_to_original(self, pi: PiClient) -> None:
        original = collect_chord_notes(pi)
        original_classes = {n % 12 for n in original}
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.2)

        for _ in range(12):
            pi.event("RIGHT_STICK_Y_POLAR", "POSITIVE")
            time.sleep(0.05)
        time.sleep(0.2)

        wrapped = collect_chord_notes(pi)
        wrapped_classes = {n % 12 for n in wrapped}
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.1)

        assert wrapped_classes == original_classes, (
            f"After 12 semitones, expected {original_classes} but got {wrapped_classes}"
        )

    def test_on_off_match_after_transpose(self, pi: PiClient) -> None:
        pi.event("RIGHT_STICK_Y_POLAR", "POSITIVE")
        time.sleep(0.1)
        pi.event("RIGHT_STICK_Y_POLAR", "POSITIVE")
        time.sleep(0.1)

        on_events, off_events = play_and_release(pi)
        on_notes = sorted(e["note_number"] for e in on_events)
        off_notes = sorted(e["note_number"] for e in off_events)
        assert len(on_notes) > 0
        assert on_notes == off_notes

    def test_all_buttons_shift_equally(self, pi: PiClient) -> None:
        # Collect original pitch classes for all buttons
        original: dict[str, set[int]] = {}
        for button in CHORD_BUTTONS:
            notes = collect_chord_notes(pi, button)
            original[button] = {n % 12 for n in notes}
            pi.event(button, "OFF")
            time.sleep(0.2)

        # Transpose up
        pi.event("RIGHT_STICK_Y_POLAR", "POSITIVE")
        time.sleep(0.2)

        for button in CHORD_BUTTONS:
            notes = collect_chord_notes(pi, button)
            transposed = {n % 12 for n in notes}
            pi.event(button, "OFF")
            time.sleep(0.2)

            expected = {(n + 1) % 12 for n in original[button]}
            assert transposed == expected, (
                f"{button}: expected {expected}, got {transposed}"
            )
