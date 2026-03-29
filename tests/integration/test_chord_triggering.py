"""Integration tests for chord triggering (functional test plan section 1).

Tests basic chord on/off, button queue behavior, and alternate voicings
by sending controller events to the app running on the Pi and verifying
MIDI output.
"""

from __future__ import annotations

import time

import pytest

from tests.integration.conftest import ALL_PRESETS_PARAMS, PiClient
from tests.integration.helpers import (
    CHORD_BUTTONS,
    assert_no_stuck_notes,
    note_numbers,
    note_offs,
    note_ons,
)

# ---------------------------------------------------------------------------
# 1.1 Basic Chord On/Off
# ---------------------------------------------------------------------------


class TestBasicChordOnOff:
    """Each chord button should produce note_on events when pressed and
    matching note_off events when released."""

    @pytest.mark.parametrize("button", CHORD_BUTTONS)
    def test_note_on_off_match(self, pi: PiClient, button: str) -> None:
        pi.event(button, "ON")
        time.sleep(0.3)
        pi.event(button, "OFF")
        time.sleep(0.3)

        events = pi.midi_history(types=["note_on", "note_off"])
        on_notes = sorted(note_numbers(note_ons(events)))
        off_notes = sorted(note_numbers(note_offs(events)))
        assert len(on_notes) > 0, f"{button} produced no note_on events"
        assert on_notes == off_notes, (
            f"{button}: note_on notes {on_notes} != note_off notes {off_notes}"
        )

    def test_each_button_plays_different_chord(self, pi: PiClient) -> None:
        chords: dict[str, list[int]] = {}
        for button in CHORD_BUTTONS:
            pi.clear_midi_history()
            pi.event(button, "ON")
            time.sleep(0.3)

            on_events = pi.midi_history(types=["note_on"])
            chords[button] = sorted(note_numbers(on_events))

            pi.event(button, "OFF")
            time.sleep(0.3)

        # At least some buttons should produce different note sets.
        # Compare pitch classes (mod 12) since octave may vary.
        pitch_class_sets = {
            button: frozenset(n % 12 for n in notes)
            for button, notes in chords.items()
        }
        unique_sets = set(pitch_class_sets.values())
        assert len(unique_sets) > 1, (
            f"Expected different chords from different buttons, got: {pitch_class_sets}"
        )


# ---------------------------------------------------------------------------
# 1.2 Button Queue (Multi-press)
# ---------------------------------------------------------------------------


class TestButtonQueue:
    """When multiple chord buttons are held, the last pressed wins.
    Releasing it should resume the previous chord."""

    def test_last_pressed_wins(self, pi: PiClient) -> None:
        # Press SOUTH, capture its chord
        pi.event("SOUTH_BUTTON", "ON")
        time.sleep(0.3)
        south_events = pi.midi_history(types=["note_on"])
        south_notes = sorted(note_numbers(south_events))

        # Now press WEST on top — should switch to WEST chord
        pi.clear_midi_history()
        pi.event("WEST_BUTTON", "ON")
        time.sleep(0.3)

        events = pi.midi_history(types=["note_on", "note_off"])
        # Should have note_offs for SOUTH and note_ons for WEST
        new_on_notes = sorted(note_numbers(note_ons(events)))
        assert new_on_notes != south_notes, "WEST chord should differ from SOUTH chord"

        # Cleanup
        pi.event("WEST_BUTTON", "OFF")
        time.sleep(0.1)
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.1)

    def test_release_resumes_previous(self, pi: PiClient) -> None:
        # Press SOUTH, get its notes
        pi.event("SOUTH_BUTTON", "ON")
        time.sleep(0.3)
        south_notes = sorted(note_numbers(pi.midi_history(types=["note_on"])))

        # Press WEST on top
        pi.event("WEST_BUTTON", "ON")
        time.sleep(0.3)

        # Release WEST — SOUTH should resume
        pi.clear_midi_history()
        pi.event("WEST_BUTTON", "OFF")
        time.sleep(0.3)

        events = pi.midi_history(types=["note_on"])
        resumed_notes = sorted(note_numbers(events))
        assert resumed_notes == south_notes, (
            f"Expected SOUTH to resume with {south_notes}, got {resumed_notes}"
        )

        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.1)

    def test_rapid_switching_no_stuck_notes(self, pi: PiClient) -> None:
        """Press/release buttons quickly and verify no stuck notes."""
        for _ in range(3):
            for button in CHORD_BUTTONS:
                pi.event(button, "ON")
                time.sleep(0.05)
                pi.event(button, "OFF")
                time.sleep(0.05)

        time.sleep(0.3)
        events = pi.midi_history(count=500, types=["note_on", "note_off"])
        assert_no_stuck_notes(events, "rapid switching")


# ---------------------------------------------------------------------------
# 1.3 Alternate Voicing
# ---------------------------------------------------------------------------


class TestAlternateVoicing:
    """RIGHT_TRIGGER toggles alternate chord voicings."""

    def test_alternate_produces_different_notes(self, pi: PiClient) -> None:
        # Get main voicing
        pi.event("SOUTH_BUTTON", "ON")
        time.sleep(0.3)
        main_notes = sorted(note_numbers(pi.midi_history(types=["note_on"])))
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.3)

        # Enable alternate
        pi.clear_midi_history()
        pi.event("RIGHT_TRIGGER", "ON")
        time.sleep(0.1)

        pi.event("SOUTH_BUTTON", "ON")
        time.sleep(0.3)
        alt_notes = sorted(note_numbers(pi.midi_history(types=["note_on"])))
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.1)

        # Disable alternate
        pi.event("RIGHT_TRIGGER", "OFF")
        time.sleep(0.1)

        # Compare pitch classes — alternate should differ
        main_classes = sorted({n % 12 for n in main_notes})
        alt_classes = sorted({n % 12 for n in alt_notes})
        assert main_classes != alt_classes, (
            f"Alternate voicing should produce different pitch classes: "
            f"main={main_classes}, alt={alt_classes}"
        )

    def test_alternate_reverts_on_release(self, pi: PiClient) -> None:
        # Get main voicing
        pi.event("SOUTH_BUTTON", "ON")
        time.sleep(0.3)
        main_notes = sorted(note_numbers(pi.midi_history(types=["note_on"])))
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.3)

        # Toggle alternate on then off
        pi.event("RIGHT_TRIGGER", "ON")
        time.sleep(0.1)
        pi.event("RIGHT_TRIGGER", "OFF")
        time.sleep(0.1)

        # Play chord again — should be back to main
        pi.clear_midi_history()
        pi.event("SOUTH_BUTTON", "ON")
        time.sleep(0.3)
        reverted_notes = sorted(note_numbers(pi.midi_history(types=["note_on"])))
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.1)

        assert reverted_notes == main_notes, (
            f"After releasing alternate, expected {main_notes} but got {reverted_notes}"
        )


# ---------------------------------------------------------------------------
# Preset parametrization - run basic checks across all presets
# ---------------------------------------------------------------------------


class TestChordTriggeringAcrossPresets:
    """Verify fundamental chord triggering works with every preset."""

    @pytest.mark.parametrize("preset_index", ALL_PRESETS_PARAMS)
    def test_chord_on_off_per_preset(self, pi: PiClient, preset_index: int) -> None:
        result = pi.load_preset(preset_index)
        assert result.get("status") == "ok", f"Failed to load preset {preset_index}: {result}"
        time.sleep(0.2)

        pi.clear_midi_history()
        pi.event("SOUTH_BUTTON", "ON")
        time.sleep(0.3)
        pi.event("SOUTH_BUTTON", "OFF")
        time.sleep(0.3)

        events = pi.midi_history(types=["note_on", "note_off"])
        on_notes = sorted(note_numbers(note_ons(events)))
        off_notes = sorted(note_numbers(note_offs(events)))

        assert len(on_notes) > 0, "No note_on events produced"
        assert on_notes == off_notes, f"note_on {on_notes} != note_off {off_notes}"

    @pytest.mark.parametrize("preset_index", ALL_PRESETS_PARAMS)
    def test_no_stuck_notes_per_preset(self, pi: PiClient, preset_index: int) -> None:
        result = pi.load_preset(preset_index)
        assert result.get("status") == "ok"
        time.sleep(0.2)

        pi.clear_midi_history()
        for button in CHORD_BUTTONS:
            pi.event(button, "ON")
            time.sleep(0.15)
            pi.event(button, "OFF")
            time.sleep(0.15)

        events = pi.midi_history(count=200, types=["note_on", "note_off"])
        assert_no_stuck_notes(events, f"preset {preset_index}")
