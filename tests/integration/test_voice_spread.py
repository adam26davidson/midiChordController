"""Integration tests for voice count and spread (functional test plan sections 5-6).

Voice count: LEFT_STICK_X_POLAR POSITIVE/NEGATIVE (1-10 range).
Spread: RIGHT_STICK_X_POLAR POSITIVE/NEGATIVE (widens/narrows note range).
"""

from __future__ import annotations

import time

from tests.integration.conftest import PiClient
from tests.integration.helpers import (
    assert_notes_in_range,
    collect_chord_notes,
    play_and_release,
)


class TestVoiceCount:

    def test_increase_produces_more_notes(self, pi: PiClient) -> None:
        original = collect_chord_notes(pi)
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.2)

        pi.event("LEFT_STICK_X_POLAR", "POSITIVE")
        time.sleep(0.2)

        increased = collect_chord_notes(pi)
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.1)

        assert len(increased) >= len(original), (
            f"Expected more notes: {len(original)} -> {len(increased)}"
        )

    def test_decrease_produces_fewer_notes(self, pi: PiClient) -> None:
        original = collect_chord_notes(pi)
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.2)

        pi.event("LEFT_STICK_X_POLAR", "NEGATIVE")
        time.sleep(0.2)

        decreased = collect_chord_notes(pi)
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.1)

        assert len(decreased) <= len(original), (
            f"Expected fewer notes: {len(original)} -> {len(decreased)}"
        )

    def test_minimum_is_one(self, pi: PiClient) -> None:
        # Decrease many times to hit minimum
        for _ in range(15):
            pi.event("LEFT_STICK_X_POLAR", "NEGATIVE")
            time.sleep(0.05)
        time.sleep(0.2)

        notes = collect_chord_notes(pi)
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.1)

        assert len(notes) >= 1, "Voice count minimum should be at least 1"

    def test_maximum_is_ten(self, pi: PiClient) -> None:
        # Increase many times to hit maximum
        for _ in range(15):
            pi.event("LEFT_STICK_X_POLAR", "POSITIVE")
            time.sleep(0.05)
        time.sleep(0.2)

        notes = collect_chord_notes(pi)
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.1)

        assert len(notes) <= 10, f"Voice count maximum should be 10, got {len(notes)}"


class TestSpread:

    def test_increase_widens_range(self, pi: PiClient) -> None:
        original = collect_chord_notes(pi)
        original_range = max(original) - min(original) if len(original) > 1 else 0
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.2)

        pi.event("RIGHT_STICK_X_POLAR", "POSITIVE")
        time.sleep(0.2)

        widened = collect_chord_notes(pi)
        widened_range = max(widened) - min(widened) if len(widened) > 1 else 0
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.1)

        assert widened_range >= original_range, (
            f"Spread increase should widen range: {original_range} -> {widened_range}"
        )

    def test_decrease_narrows_range(self, pi: PiClient) -> None:
        # First increase spread so we have room to decrease
        for _ in range(3):
            pi.event("RIGHT_STICK_X_POLAR", "POSITIVE")
            time.sleep(0.05)
        time.sleep(0.2)

        wide = collect_chord_notes(pi)
        wide_range = max(wide) - min(wide) if len(wide) > 1 else 0
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.2)

        pi.event("RIGHT_STICK_X_POLAR", "NEGATIVE")
        time.sleep(0.2)

        narrow = collect_chord_notes(pi)
        narrow_range = max(narrow) - min(narrow) if len(narrow) > 1 else 0
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.1)

        assert narrow_range <= wide_range, (
            f"Spread decrease should narrow range: {wide_range} -> {narrow_range}"
        )

    def test_extreme_spread_stays_in_midi_range(self, pi: PiClient) -> None:
        # Max out spread
        for _ in range(30):
            pi.event("RIGHT_STICK_X_POLAR", "POSITIVE")
            time.sleep(0.05)
        time.sleep(0.2)

        on_events, _ = play_and_release(pi)
        assert_notes_in_range(on_events, low=0, high=127, context="max spread")
