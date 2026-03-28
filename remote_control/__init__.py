from __future__ import annotations

import asyncio
import json
import logging
from typing import TYPE_CHECKING, Callable

from controller_manager.models.control_event import ControlEvent
from controller_manager.models.mappable_control_event import MappableControlEvent

if TYPE_CHECKING:
    from music_engine.midi import Midi
    from music_engine.midi.midi_history import MidiHistory

logger = logging.getLogger(__name__)

REMOTE_CONTROL_DEFAULT_PORT = 9999


class RemoteControlServer:

    _callback: Callable[[ControlEvent], None]
    _midi: Midi | None
    _midi_history: MidiHistory | None
    _port: int
    _server: asyncio.Server | None

    def __init__(
        self,
        callback: Callable[[ControlEvent], None],
        port: int = REMOTE_CONTROL_DEFAULT_PORT,
        midi_history: MidiHistory | None = None,
        midi: Midi | None = None,
    ) -> None:
        self._callback = callback
        self._port = port
        self._server = None
        self._midi_history = midi_history
        self._midi = midi

    def start(self) -> None:
        asyncio.ensure_future(self._start_server())

    async def _start_server(self) -> None:
        import socket as _socket

        self._server = await asyncio.start_server(
            self._handle_client,
            "0.0.0.0",
            self._port,
            reuse_address=True,
            start_serving=False,
        )
        # Set SO_REUSEPORT on each socket so restarts don't fail with "address in use"
        for sock in self._server.sockets or []:
            sock.setsockopt(_socket.SOL_SOCKET, _socket.SO_REUSEADDR, 1)
        await self._server.start_serving()
        logger.info("Remote control server listening on port %d", self._port)

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        peer = writer.get_extra_info("peername")
        logger.info("Remote control client connected: %s", peer)
        try:
            while True:
                line = await reader.readline()
                if not line:
                    break
                response = self._process_line(line.decode().strip())
                if response is not None:
                    writer.write((json.dumps(response) + "\n").encode())
                    await writer.drain()
        except ConnectionResetError:
            pass
        finally:
            writer.close()
            logger.info("Remote control client disconnected: %s", peer)

    def _process_line(self, line: str) -> dict[str, object] | None:
        if not line:
            return None
        try:
            data: dict[str, object] = json.loads(line)
        except json.JSONDecodeError:
            logger.warning("Remote control: invalid JSON: %s", line)
            return None

        # Query messages return a response
        if "query" in data:
            return self._handle_query(data)

        # MIDI input messages (fire-and-forget)
        if "midi_in" in data:
            self._handle_midi_in(data)
            return None

        # Controller event messages (fire-and-forget)
        self._handle_event(data)
        return None

    def _handle_event(self, data: dict[str, object]) -> None:
        control_key = data.get("control_key")
        event_name = data.get("event")

        if not isinstance(control_key, str) or not isinstance(event_name, str):
            logger.warning("Remote control: missing control_key or event: %s", data)
            return

        try:
            event = MappableControlEvent[event_name]
        except KeyError:
            logger.warning("Remote control: unknown event type '%s'", event_name)
            return

        raw_value = data.get("value")
        value: float | None = None
        if raw_value is not None and isinstance(raw_value, (int, float, str)):
            value = float(raw_value)

        control_event = ControlEvent(
            control_key=control_key,
            event=event,
            controller_id="remote",
            value=value,
        )
        logger.debug("Remote control event: %s %s %s", control_key, event_name, value)
        self._callback(control_event)

    # MIDI status byte constants
    _NOTE_ON = 0x90
    _NOTE_OFF = 0x80

    def _handle_midi_in(self, data: dict[str, object]) -> None:
        if self._midi is None:
            logger.warning("Remote control: MIDI input not available")
            return

        midi_type = data.get("midi_in")
        if not isinstance(midi_type, str):
            logger.warning("Remote control: invalid midi_in type: %s", data)
            return

        raw_note = data.get("note")
        if not isinstance(raw_note, (int, float)):
            logger.warning("Remote control: missing or invalid note: %s", data)
            return
        note = int(raw_note)

        raw_channel = data.get("channel", 0)
        channel = int(raw_channel) if isinstance(raw_channel, (int, float)) else 0

        if midi_type == "note_on":
            raw_velocity = data.get("velocity", 100)
            velocity = int(raw_velocity) if isinstance(raw_velocity, (int, float)) else 100
            status = self._NOTE_ON | (channel & 0x0F)
            midi_message = [status, note, velocity]
        elif midi_type == "note_off":
            status = self._NOTE_OFF | (channel & 0x0F)
            midi_message = [status, note, 0]
        else:
            logger.warning("Remote control: unknown midi_in type '%s'", midi_type)
            return

        logger.debug("Remote control MIDI in: %s note=%d ch=%d", midi_type, note, channel)
        self._midi.handle_midi_in((midi_message, 0.0), "remote")

    def _handle_query(self, data: dict[str, object]) -> dict[str, object]:
        query = data.get("query")

        if query == "midi_history":
            if self._midi_history is None:
                return {"error": "MIDI history not available"}
            raw_count = data.get("count", 50)
            count = int(raw_count) if isinstance(raw_count, (int, float, str)) else 50
            raw_types = data.get("types")
            types: list[str] | None = [str(t) for t in raw_types] if isinstance(raw_types, list) else None
            raw_since = data.get("since")
            since = float(raw_since) if isinstance(raw_since, (int, float, str)) else None
            events = self._midi_history.get(count=count, types=types, since=since)
            return {"events": events}

        if query == "midi_history_clear":
            if self._midi_history is None:
                return {"error": "MIDI history not available"}
            self._midi_history.clear()
            return {"status": "cleared"}

        return {"error": f"Unknown query: {query}"}
