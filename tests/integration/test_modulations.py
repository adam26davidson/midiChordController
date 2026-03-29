"""Integration tests for modulations and secondaries (functional test plan sections 9-10).

Modulations: LEFT_BUMPER (left), RIGHT_BUMPER (right) — scale transformations.
Secondaries: DPAD_X_LEFT (left), DPAD_X_RIGHT (right) — chromatic chord overlays.
"""

from __future__ import annotations

import time

from tests.integration.conftest import PiClient
from tests.integration.helpers import (
    assert_no_stuck_notes,
    collect_chord_notes,
    pitch_classes,
    play_and_release,
)


class TestModulations:

    def test_left_modulation_changes_pitch_classes(self, pi: PiClient) -> None:
        on_orig, _ = play_and_release(pi)
        original_pc = pitch_classes(on_orig)

        pi.event("LEFT_BUMPER", "ON")
        time.sleep(0.2)

        on_mod, _ = play_and_release(pi)
        mod_pc = pitch_classes(on_mod)

        pi.event("LEFT_BUMPER", "OFF")
        time.sleep(0.1)

        assert mod_pc != original_pc, (
            f"Left modulation should change pitch classes: {original_pc} vs {mod_pc}"
        )

    def test_left_modulation_off_reverts(self, pi: PiClient) -> None:
        original = collect_chord_notes(pi)
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.2)

        pi.event("LEFT_BUMPER", "ON")
        time.sleep(0.1)
        pi.event("LEFT_BUMPER", "OFF")
        time.sleep(0.2)

        reverted = collect_chord_notes(pi)
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.1)

        assert reverted == original, (
            f"Left mod off should revert: {original} vs {reverted}"
        )

    def test_right_modulation_changes_pitch_classes(self, pi: PiClient) -> None:
        on_orig, _ = play_and_release(pi)
        original_pc = pitch_classes(on_orig)

        pi.event("RIGHT_BUMPER", "ON")
        time.sleep(0.2)

        on_mod, _ = play_and_release(pi)
        mod_pc = pitch_classes(on_mod)

        pi.event("RIGHT_BUMPER", "OFF")
        time.sleep(0.1)

        assert mod_pc != original_pc, (
            f"Right modulation should change pitch classes: {original_pc} vs {mod_pc}"
        )

    def test_left_and_right_modulations_differ(self, pi: PiClient) -> None:
        pi.event("LEFT_BUMPER", "ON")
        time.sleep(0.2)
        on_left, _ = play_and_release(pi)
        left_pc = pitch_classes(on_left)
        pi.event("LEFT_BUMPER", "OFF")
        time.sleep(0.2)

        pi.event("RIGHT_BUMPER", "ON")
        time.sleep(0.2)
        on_right, _ = play_and_release(pi)
        right_pc = pitch_classes(on_right)
        pi.event("RIGHT_BUMPER", "OFF")
        time.sleep(0.1)

        assert left_pc != right_pc, (
            f"Left and right modulations should differ: {left_pc} vs {right_pc}"
        )

    def test_no_stuck_notes_through_modulation_toggle(self, pi: PiClient) -> None:
        pi.event("SOUTH_BUTTON", "ON")
        time.sleep(0.2)

        pi.event("LEFT_BUMPER", "ON")
        time.sleep(0.2)
        pi.event("LEFT_BUMPER", "OFF")
        time.sleep(0.2)

        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.3)

        events = pi.midi_history(count=200, types=["note_on", "note_off"])
        assert_no_stuck_notes(events, "modulation toggle")


class TestSecondaryChords:

    def test_left_secondary_changes_pitch_classes(self, pi: PiClient) -> None:
        on_orig, _ = play_and_release(pi)
        original_pc = pitch_classes(on_orig)

        pi.event("DPAD_X_LEFT", "ON")
        time.sleep(0.2)

        on_sec, _ = play_and_release(pi)
        sec_pc = pitch_classes(on_sec)

        pi.event("DPAD_X_LEFT", "OFF")
        time.sleep(0.1)

        assert sec_pc != original_pc, (
            f"Left secondary should change pitch classes: {original_pc} vs {sec_pc}"
        )

    def test_left_secondary_off_reverts(self, pi: PiClient) -> None:
        original = collect_chord_notes(pi)
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.2)

        pi.event("DPAD_X_LEFT", "ON")
        time.sleep(0.1)
        pi.event("DPAD_X_LEFT", "OFF")
        time.sleep(0.2)

        reverted = collect_chord_notes(pi)
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.1)

        assert reverted == original

    def test_right_secondary_changes_pitch_classes(self, pi: PiClient) -> None:
        on_orig, _ = play_and_release(pi)
        original_pc = pitch_classes(on_orig)

        pi.event("DPAD_X_RIGHT", "ON")
        time.sleep(0.2)

        on_sec, _ = play_and_release(pi)
        sec_pc = pitch_classes(on_sec)

        pi.event("DPAD_X_RIGHT", "OFF")
        time.sleep(0.1)

        assert sec_pc != original_pc, (
            f"Right secondary should change pitch classes: {original_pc} vs {sec_pc}"
        )
