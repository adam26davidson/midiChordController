#!/usr/bin/env python3
"""Standalone sender script for the remote control server. No project dependencies required."""

from __future__ import annotations

import argparse
import json
import socket
import sys
import time

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 9999


def send_lines(host: str, port: int, lines: list[str]) -> None:
    with socket.create_connection((host, port), timeout=5) as sock:
        for line in lines:
            sock.sendall((line + "\n").encode())
        time.sleep(0.05)


def cmd_press(args: argparse.Namespace) -> None:
    duration = args.duration / 1000.0
    on = json.dumps({"control_key": args.key, "event": "ON"})
    off = json.dumps({"control_key": args.key, "event": "OFF"})
    with socket.create_connection((args.host, args.port), timeout=5) as sock:
        sock.sendall((on + "\n").encode())
        time.sleep(duration)
        sock.sendall((off + "\n").encode())
        time.sleep(0.05)


def cmd_event(args: argparse.Namespace) -> None:
    msg: dict[str, str | float | None] = {
        "control_key": args.key,
        "event": args.event_type,
    }
    if args.value is not None:
        msg["value"] = args.value
    send_lines(args.host, args.port, [json.dumps(msg)])


def cmd_analog(args: argparse.Namespace) -> None:
    msg = json.dumps({
        "control_key": args.key,
        "event": "UPDATE",
        "value": args.value,
    })
    send_lines(args.host, args.port, [msg])


# All buttons that can be in an ON state
BUTTONS = [
    "SOUTH_BUTTON", "WEST_BUTTON", "NORTH_BUTTON", "EAST_BUTTON",
    "DPAD_X_LEFT", "DPAD_X_RIGHT", "DPAD_Y_UP", "DPAD_Y_DOWN",
    "RIGHT_BUMPER", "LEFT_BUMPER",
    "RIGHT_TRIGGER", "LEFT_TRIGGER",
    "LEFT_OPTION", "RIGHT_OPTION",
    "RIGHT_STICK_BUTTON", "LEFT_STICK_BUTTON",
    "START_BUTTON",
]

# Analog controls and their neutral values
ANALOGS = [
    "GYRO_PITCH", "GYRO_ROLL",
    "LEFT_STICK_X_POLAR", "LEFT_STICK_Y_POLAR",
    "RIGHT_STICK_X_POLAR", "RIGHT_STICK_Y_POLAR",
    "TOUCHPAD_X", "TOUCHPAD_Y",
    "DPAD_Y",
]


def cmd_reset(args: argparse.Namespace) -> None:
    lines: list[str] = []
    # Send OFF for all buttons
    for key in BUTTONS:
        lines.append(json.dumps({"control_key": key, "event": "OFF"}))
    # Reset all analogs to 0
    for key in ANALOGS:
        lines.append(json.dumps({"control_key": key, "event": "UPDATE", "value": 0.0}))
    send_lines(args.host, args.port, lines)


def send_query(host: str, port: int, query: dict[str, object]) -> str:
    """Send a query and return the JSON response."""
    with socket.create_connection((host, port), timeout=5) as sock:
        sock.sendall((json.dumps(query) + "\n").encode())
        # Read until we get a complete line (the response)
        response = b""
        while b"\n" not in response:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk
        return response.decode().strip()


def cmd_midi(args: argparse.Namespace) -> None:
    query: dict[str, object] = {"query": "midi_history", "count": args.count}
    if args.types:
        query["types"] = args.types.split(",")
    result = send_query(args.host, args.port, query)
    print(result)


def cmd_midi_in(args: argparse.Namespace) -> None:
    msg: dict[str, str | int] = {"midi_in": args.midi_type, "note": args.note}
    if args.velocity is not None:
        msg["velocity"] = args.velocity
    if args.channel is not None:
        msg["channel"] = args.channel
    send_lines(args.host, args.port, [json.dumps(msg)])


def main() -> None:
    parser = argparse.ArgumentParser(description="Send events to the remote control server")
    parser.add_argument("--host", default=DEFAULT_HOST, help=f"Server host (default: {DEFAULT_HOST})")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Server port (default: {DEFAULT_PORT})")

    subparsers = parser.add_subparsers(dest="command", required=True)

    p_press = subparsers.add_parser("press", help="Press and release a button")
    p_press.add_argument("key", help="Control key (e.g. SOUTH_BUTTON)")
    p_press.add_argument("--duration", type=int, default=100, help="Hold duration in ms (default: 100)")

    p_event = subparsers.add_parser("event", help="Send a single raw event")
    p_event.add_argument("key", help="Control key")
    p_event.add_argument("event_type", help="Event type: ON, OFF, POSITIVE, NEGATIVE, UPDATE")
    p_event.add_argument("value", type=float, nargs="?", default=None, help="Value for UPDATE events")

    p_analog = subparsers.add_parser("analog", help="Send an analog UPDATE event")
    p_analog.add_argument("key", help="Control key (e.g. GYRO_PITCH)")
    p_analog.add_argument("value", type=float, help="Analog value (-1.0 to 1.0)")

    subparsers.add_parser("reset", help="Release all buttons and zero all analog controls")

    p_midi = subparsers.add_parser("midi", help="Query MIDI output history")
    p_midi.add_argument("--count", type=int, default=50, help="Number of events (default: 50)")
    p_midi.add_argument("--types", default=None, help="Comma-separated filter: note_on,note_off,aftertouch,poly_aftertouch,control_change")

    p_midi_in = subparsers.add_parser("midi_in", help="Send MIDI input to the app")
    p_midi_in.add_argument("midi_type", help="note_on or note_off")
    p_midi_in.add_argument("note", type=int, help="MIDI note number (0-127)")
    p_midi_in.add_argument("velocity", type=int, nargs="?", default=100, help="Velocity for note_on (default: 100)")
    p_midi_in.add_argument("--channel", type=int, default=0, help="MIDI channel (default: 0)")

    args = parser.parse_args()

    try:
        if args.command == "press":
            cmd_press(args)
        elif args.command == "event":
            cmd_event(args)
        elif args.command == "analog":
            cmd_analog(args)
        elif args.command == "reset":
            cmd_reset(args)
        elif args.command == "midi":
            cmd_midi(args)
        elif args.command == "midi_in":
            cmd_midi_in(args)
    except ConnectionRefusedError:
        print(f"Error: could not connect to {args.host}:{args.port}. Is the app running with --remote-control?", file=sys.stderr)
        sys.exit(1)
    except socket.timeout:
        print(f"Error: connection to {args.host}:{args.port} timed out.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
