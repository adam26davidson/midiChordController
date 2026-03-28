from __future__ import annotations

import time
from collections import deque
from enum import Enum
from typing import TypedDict


class MidiEventType(Enum):
    NOTE_ON = "note_on"
    NOTE_OFF = "note_off"
    AFTERTOUCH = "aftertouch"
    POLY_AFTERTOUCH = "poly_aftertouch"
    CONTROL_CHANGE = "control_change"
    UNKNOWN = "unknown"


# MIDI status byte to event type mapping
_STATUS_TO_TYPE: dict[int, MidiEventType] = {
    0x90: MidiEventType.NOTE_ON,
    0x80: MidiEventType.NOTE_OFF,
    0xD0: MidiEventType.AFTERTOUCH,
    0xA0: MidiEventType.POLY_AFTERTOUCH,
    0xB0: MidiEventType.CONTROL_CHANGE,
}

# Note names for display
_NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def _note_name(midi_note: int) -> str:
    octave = (midi_note // 12) - 1
    return f"{_NOTE_NAMES[midi_note % 12]}{octave}"


class MidiHistoryEntry(TypedDict):
    type: str
    channel: int
    note: str | None
    note_number: int | None
    velocity: int | None
    value: int | None
    cc: int | None
    timestamp: float


MAX_HISTORY = 500


class MidiHistory:
    """Ring buffer of recent MIDI output messages."""

    _history: deque[MidiHistoryEntry]

    def __init__(self) -> None:
        self._history = deque(maxlen=MAX_HISTORY)

    def record(self, message: list[int]) -> None:
        status = message[0] & 0xF0
        channel = message[0] & 0x0F
        event_type = _STATUS_TO_TYPE.get(status, MidiEventType.UNKNOWN)

        # NOTE_ON with velocity 0 is actually a NOTE_OFF
        if event_type == MidiEventType.NOTE_ON and len(message) > 2 and message[2] == 0:
            event_type = MidiEventType.NOTE_OFF

        entry: MidiHistoryEntry = {
            "type": event_type.value,
            "channel": channel,
            "note": None,
            "note_number": None,
            "velocity": None,
            "value": None,
            "cc": None,
            "timestamp": time.time(),
        }

        if event_type in (MidiEventType.NOTE_ON, MidiEventType.NOTE_OFF):
            entry["note"] = _note_name(message[1])
            entry["note_number"] = message[1]
            if len(message) > 2:
                entry["velocity"] = message[2]

        elif event_type == MidiEventType.AFTERTOUCH:
            entry["value"] = message[1] if len(message) > 1 else None

        elif event_type == MidiEventType.POLY_AFTERTOUCH:
            entry["note"] = _note_name(message[1])
            entry["note_number"] = message[1]
            entry["value"] = message[2] if len(message) > 2 else None

        elif event_type == MidiEventType.CONTROL_CHANGE:
            entry["cc"] = message[1] if len(message) > 1 else None
            entry["value"] = message[2] if len(message) > 2 else None

        self._history.append(entry)

    def get(
        self,
        count: int = 50,
        types: list[str] | None = None,
        since: float | None = None,
    ) -> list[MidiHistoryEntry]:
        """Return recent MIDI events, optionally filtered.

        Args:
            count: Max number of events to return.
            types: Filter by event type (e.g. ["note_on", "note_off"]).
            since: Only return events after this unix timestamp.
        """
        result: list[MidiHistoryEntry] = []
        for entry in reversed(self._history):
            if since is not None and entry["timestamp"] < since:
                break
            if types is not None and entry["type"] not in types:
                continue
            result.append(entry)
            if len(result) >= count:
                break
        result.reverse()
        return result

    def clear(self) -> None:
        self._history.clear()
