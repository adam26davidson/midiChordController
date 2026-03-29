"""Integration tests for inversion (functional test plan section 3).

Inversion rearranges chord voice octaves without changing pitch classes.
Control: GYRO_PITCH UPDATE (float -1.0 to 1.0).
Inversion lock: LEFT_OPTION (toggle).
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


class TestInversion:

    def test_different_gyro_values_change_voicing(self, pi: PiClient) -> None:
        pi.analog("GYRO_PITCH", -0.9)
        time.sleep(0.2)
        notes_low = collect_chord_notes(pi)
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.2)

        pi.analog("GYRO_PITCH", 0.9)
        time.sleep(0.2)
        notes_high = collect_chord_notes(pi)
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.1)

        assert notes_low != notes_high, (
            f"Different inversion values should produce different voicings: "
            f"{notes_low} vs {notes_high}"
        )

    def test_pitch_classes_preserved(self, pi: PiClient) -> None:
        pi.analog("GYRO_PITCH", 0.0)
        time.sleep(0.2)
        on_zero, _ = play_and_release(pi)

        pi.analog("GYRO_PITCH", 0.6)
        time.sleep(0.2)
        on_high, _ = play_and_release(pi)

        assert pitch_classes(on_zero) == pitch_classes(on_high), (
            f"Inversion should preserve pitch classes: "
            f"{pitch_classes(on_zero)} vs {pitch_classes(on_high)}"
        )

    def test_on_off_match_across_inversions(self, pi: PiClient) -> None:
        pi.analog("GYRO_PITCH", 0.5)
        time.sleep(0.2)

        on_events, off_events = play_and_release(pi)
        on_notes = sorted(e["note_number"] for e in on_events)
        off_notes = sorted(e["note_number"] for e in off_events)
        assert len(on_notes) > 0
        assert on_notes == off_notes


class TestInversionLock:

    def test_lock_prevents_inversion_change(self, pi: PiClient) -> None:
        pi.analog("GYRO_PITCH", -0.9)
        time.sleep(0.2)
        notes_before = collect_chord_notes(pi)
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.2)

        # Toggle lock on (LEFT_OPTION ON sends TOGGLE command)
        pi.event("LEFT_OPTION", "ON")
        time.sleep(0.2)

        # Change GYRO_PITCH — should have no effect while locked
        pi.analog("GYRO_PITCH", 0.9)
        time.sleep(0.2)
        notes_locked = collect_chord_notes(pi)
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.1)

        assert notes_before == notes_locked, (
            f"Lock should prevent inversion change: {notes_before} vs {notes_locked}"
        )

    def test_unlock_restores_responsiveness(self, pi: PiClient) -> None:
        # Set inversion to one extreme
        pi.analog("GYRO_PITCH", -0.9)
        time.sleep(0.2)
        notes_at_low = collect_chord_notes(pi)
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.2)

        # Lock, then unlock (two toggles)
        pi.event("LEFT_OPTION", "ON")
        time.sleep(0.1)
        pi.event("LEFT_OPTION", "ON")
        time.sleep(0.2)

        # Move to opposite extreme — should take effect since unlocked
        pi.analog("GYRO_PITCH", 0.9)
        time.sleep(0.2)
        notes_at_high = collect_chord_notes(pi)
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.1)

        assert notes_at_low != notes_at_high, (
            f"After unlock, GYRO_PITCH should change voicing: "
            f"low={notes_at_low} vs high={notes_at_high}"
        )

    def test_no_stuck_notes_through_lock_toggle(self, pi: PiClient) -> None:
        pi.analog("GYRO_PITCH", 0.3)
        time.sleep(0.1)
        pi.event("SOUTH_BUTTON", "ON")
        time.sleep(0.2)

        # Toggle lock on/off while chord is playing
        pi.event("LEFT_OPTION", "ON")
        time.sleep(0.1)
        pi.event("LEFT_OPTION", "ON")
        time.sleep(0.1)

        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.3)

        events = pi.midi_history(count=100, types=["note_on", "note_off"])
        assert_no_stuck_notes(events, "lock toggle")
