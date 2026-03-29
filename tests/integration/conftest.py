"""Integration test fixtures for testing the app running on the Raspberry Pi.

Tests communicate with the app via its remote control TCP server (port 9999).
The Pi hostname is configurable via --pi-host or the PI_HOST env var.

Usage:
    uv run pytest tests/integration/ --pi-host chord-controller
    PI_HOST=chord-controller uv run pytest tests/integration/
"""

from __future__ import annotations

import json
import os
import socket
import time
from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator

from constants import SETTINGS

DEFAULT_HOST = "chord-controller"
DEFAULT_PORT = 9999

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


class PiClient:
    """Client for the app's remote control TCP server."""

    def __init__(self, host: str, port: int = DEFAULT_PORT) -> None:
        self.host = host
        self.port = port

    def _send_lines(self, lines: list[str]) -> None:
        with socket.create_connection((self.host, self.port), timeout=5) as sock:
            for line in lines:
                sock.sendall((line + "\n").encode())
            time.sleep(0.05)

    def _query(self, query: dict[str, object]) -> dict[str, Any]:
        with socket.create_connection((self.host, self.port), timeout=5) as sock:
            sock.sendall((json.dumps(query) + "\n").encode())
            response = b""
            while b"\n" not in response:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
            return json.loads(response.decode().strip())

    # -- Controller events --

    def event(self, control_key: str, event_type: str, value: float | None = None) -> None:
        msg: dict[str, str | float] = {"control_key": control_key, "event": event_type}
        if value is not None:
            msg["value"] = value
        self._send_lines([json.dumps(msg)])

    def press(self, control_key: str, duration_ms: int = 100) -> None:
        with socket.create_connection((self.host, self.port), timeout=5) as sock:
            sock.sendall((json.dumps({"control_key": control_key, "event": "ON"}) + "\n").encode())
            time.sleep(duration_ms / 1000.0)
            sock.sendall((json.dumps({"control_key": control_key, "event": "OFF"}) + "\n").encode())
            time.sleep(0.05)

    def analog(self, control_key: str, value: float) -> None:
        self.event(control_key, "UPDATE", value)

    def reset(self) -> None:
        lines: list[str] = []
        for key in BUTTONS:
            lines.append(json.dumps({"control_key": key, "event": "OFF"}))
        for key in ANALOGS:
            lines.append(json.dumps({"control_key": key, "event": "UPDATE", "value": 0.0}))
        self._send_lines(lines)

    # -- MIDI queries --

    def midi_history(
        self,
        count: int = 50,
        types: list[str] | None = None,
        since: float | None = None,
    ) -> list[dict[str, Any]]:
        query: dict[str, object] = {"query": "midi_history", "count": count}
        if types is not None:
            query["types"] = types
        if since is not None:
            query["since"] = since
        result = self._query(query)
        return result.get("events", [])

    def clear_midi_history(self) -> None:
        self._query({"query": "midi_history_clear"})

    # -- MIDI input --

    def midi_in(self, note: int, midi_type: str = "note_on", velocity: int = 100, channel: int = 0) -> None:
        msg: dict[str, str | int] = {"midi_in": midi_type, "note": note, "channel": channel}
        if midi_type == "note_on":
            msg["velocity"] = velocity
        self._send_lines([json.dumps(msg)])

    # -- Preset management --

    def load_preset(self, preset: int | str) -> dict[str, Any]:
        return self._query({"query": "load_preset", "preset": preset})

    def preset_list(self) -> list[dict[str, Any]]:
        result = self._query({"query": "preset_list"})
        return result.get("presets", [])

    def reset_engine_state(self) -> dict[str, Any]:
        """Reset all engine state to defaults and reload preset 0."""
        return self._query({"query": "reset_engine_state"})

    # -- Convenience --

    def collect_midi(
        self,
        action: str,
        *,
        settle_ms: int = 300,
        count: int = 50,
        types: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Clear MIDI history, perform an action string, wait, then return MIDI events.

        Action format: "SOUTH_BUTTON ON", "GYRO_PITCH UPDATE 0.5", etc.
        """
        self.clear_midi_history()
        parts = action.split()
        control_key = parts[0]
        event_type = parts[1]
        value = float(parts[2]) if len(parts) > 2 else None
        self.event(control_key, event_type, value)
        time.sleep(settle_ms / 1000.0)
        return self.midi_history(count=count, types=types)


# -- Pytest configuration --


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--pi-host",
        default=os.environ.get("PI_HOST", DEFAULT_HOST),
        help=f"Hostname of the Pi running the app (default: ${DEFAULT_HOST}, or PI_HOST env var)",
    )


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "integration: tests that run against the Pi")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)


@pytest.fixture(scope="session")
def pi_host(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("--pi-host")


@pytest.fixture(scope="session")
def pi_client(pi_host: str) -> PiClient:
    client = PiClient(host=pi_host)
    # Verify connectivity
    try:
        client.preset_list()
    except (ConnectionRefusedError, socket.timeout, OSError) as e:
        pytest.skip(f"Cannot connect to Pi at {pi_host}:{DEFAULT_PORT}: {e}")
    return client


@pytest.fixture
def pi(pi_client: PiClient) -> Generator[PiClient]:
    """Per-test fixture that fully resets controller and engine state."""
    pi_client.reset()
    pi_client.reset_engine_state()
    time.sleep(0.1)
    pi_client.clear_midi_history()
    yield pi_client
    pi_client.reset()


# -- Preset parametrization --

ALL_PRESET_INDICES = list(range(len(SETTINGS)))
ALL_PRESET_NAMES = [s["name"] for s in SETTINGS]
ALL_PRESETS_PARAMS = [
    pytest.param(i, id=name) for i, name in enumerate(ALL_PRESET_NAMES)
]
