"""Shared helpers for integration tests."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from tests.integration.conftest import PiClient

CHORD_BUTTONS = ["SOUTH_BUTTON", "WEST_BUTTON", "NORTH_BUTTON", "EAST_BUTTON"]


def note_ons(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [e for e in events if e["type"] == "note_on"]


def note_offs(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [e for e in events if e["type"] == "note_off"]


def note_numbers(events: list[dict[str, Any]]) -> list[int]:
    return [e["note_number"] for e in events]


def assert_no_stuck_notes(events: list[dict[str, Any]], context: str = "") -> None:
    """Assert every note_on in the event list has at least one matching note_off.

    Extra note_offs (more offs than ons) are tolerated — they are harmless
    and can occur during rapid re-voicing. Stuck notes (more ons than offs)
    are the real problem.
    """
    on_counts: dict[int, int] = {}
    off_counts: dict[int, int] = {}
    for e in events:
        note = e["note_number"]
        if e["type"] == "note_on":
            on_counts[note] = on_counts.get(note, 0) + 1
        elif e["type"] == "note_off":
            off_counts[note] = off_counts.get(note, 0) + 1

    prefix = f"{context}: " if context else ""
    for note, count in on_counts.items():
        off = off_counts.get(note, 0)
        assert off >= count, f"{prefix}note {note}: {count} note_on but only {off} note_off (stuck note)"


def pitch_classes(events: list[dict[str, Any]]) -> set[int]:
    """Extract unique pitch classes (note % 12) from note_on events."""
    return {e["note_number"] % 12 for e in events if e["type"] == "note_on"}


def collect_chord_notes(pi: PiClient, button: str = "SOUTH_BUTTON", settle_ms: int = 300) -> list[int]:
    """Clear MIDI history, press button ON, wait, return sorted note numbers."""
    pi.clear_midi_history()
    pi.event(button, "ON")
    time.sleep(settle_ms / 1000.0)
    events = pi.midi_history(types=["note_on"])
    return sorted(note_numbers(events))


def play_and_release(
    pi: PiClient, button: str = "SOUTH_BUTTON", settle_ms: int = 300
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Full press/release cycle. Returns (note_on_events, note_off_events)."""
    pi.clear_midi_history()
    pi.event(button, "ON")
    time.sleep(settle_ms / 1000.0)
    pi.event(button, "OFF")
    time.sleep(settle_ms / 1000.0)
    events = pi.midi_history(types=["note_on", "note_off"])
    return note_ons(events), note_offs(events)


def assert_notes_in_range(
    events: list[dict[str, Any]], low: int = 21, high: int = 108, context: str = ""
) -> None:
    """Assert all note_on events have note numbers within [low, high]."""
    prefix = f"{context}: " if context else ""
    for e in events:
        if e["type"] == "note_on":
            assert low <= e["note_number"] <= high, (
                f"{prefix}note {e['note_number']} outside range [{low}, {high}]"
            )
