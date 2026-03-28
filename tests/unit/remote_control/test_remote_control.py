from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

from controller_manager.models.control_event import ControlEvent

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator
from controller_manager.models.mappable_control_event import MappableControlEvent
from remote_control import RemoteControlServer


@pytest.fixture
def callback() -> MagicMock:
    return MagicMock()


@pytest.fixture
async def server_and_port(callback: MagicMock) -> AsyncGenerator[tuple[RemoteControlServer, int], None]:
    server = RemoteControlServer(callback, port=0)
    await server._start_server()
    assert server._server is not None
    # Get the port assigned by the OS
    sockets = server._server.sockets
    assert sockets is not None
    port: int = sockets[0].getsockname()[1]
    yield server, port
    server._server.close()
    await server._server.wait_closed()


async def _send_lines(port: int, lines: list[str]) -> None:
    _reader, writer = await asyncio.open_connection("127.0.0.1", port)
    for line in lines:
        writer.write((line + "\n").encode())
    await writer.drain()
    writer.close()
    await writer.wait_closed()
    # Give the server a moment to process
    await asyncio.sleep(0.05)


@pytest.mark.asyncio
async def test_button_on_event(
    server_and_port: tuple[RemoteControlServer, int],
    callback: MagicMock,
) -> None:
    _, port = server_and_port
    await _send_lines(port, [json.dumps({"control_key": "SOUTH_BUTTON", "event": "ON"})])

    callback.assert_called_once()
    event: ControlEvent = callback.call_args[0][0]
    assert event.control_key == "SOUTH_BUTTON"
    assert event.event == MappableControlEvent.ON
    assert event.controller_id == "remote"
    assert event.value is None


@pytest.mark.asyncio
async def test_button_off_event(
    server_and_port: tuple[RemoteControlServer, int],
    callback: MagicMock,
) -> None:
    _, port = server_and_port
    await _send_lines(port, [json.dumps({"control_key": "WEST_BUTTON", "event": "OFF"})])

    callback.assert_called_once()
    event: ControlEvent = callback.call_args[0][0]
    assert event.control_key == "WEST_BUTTON"
    assert event.event == MappableControlEvent.OFF


@pytest.mark.asyncio
async def test_update_event_with_value(
    server_and_port: tuple[RemoteControlServer, int],
    callback: MagicMock,
) -> None:
    _, port = server_and_port
    await _send_lines(port, [json.dumps({"control_key": "GYRO_PITCH", "event": "UPDATE", "value": 0.75})])

    callback.assert_called_once()
    event: ControlEvent = callback.call_args[0][0]
    assert event.control_key == "GYRO_PITCH"
    assert event.event == MappableControlEvent.UPDATE
    assert event.value == 0.75


@pytest.mark.asyncio
async def test_positive_and_negative_events(
    server_and_port: tuple[RemoteControlServer, int],
    callback: MagicMock,
) -> None:
    _, port = server_and_port
    await _send_lines(port, [
        json.dumps({"control_key": "DPAD_Y_UP", "event": "POSITIVE"}),
        json.dumps({"control_key": "DPAD_Y_DOWN", "event": "NEGATIVE"}),
    ])

    assert callback.call_count == 2
    first: ControlEvent = callback.call_args_list[0][0][0]
    second: ControlEvent = callback.call_args_list[1][0][0]
    assert first.event == MappableControlEvent.POSITIVE
    assert second.event == MappableControlEvent.NEGATIVE


@pytest.mark.asyncio
async def test_multiple_events_on_one_connection(
    server_and_port: tuple[RemoteControlServer, int],
    callback: MagicMock,
) -> None:
    _, port = server_and_port
    await _send_lines(port, [
        json.dumps({"control_key": "SOUTH_BUTTON", "event": "ON"}),
        json.dumps({"control_key": "SOUTH_BUTTON", "event": "OFF"}),
    ])

    assert callback.call_count == 2


@pytest.mark.asyncio
async def test_malformed_json_is_skipped(
    server_and_port: tuple[RemoteControlServer, int],
    callback: MagicMock,
) -> None:
    _, port = server_and_port
    await _send_lines(port, [
        "not valid json",
        json.dumps({"control_key": "SOUTH_BUTTON", "event": "ON"}),
    ])

    # Malformed line skipped, valid line processed
    callback.assert_called_once()


@pytest.mark.asyncio
async def test_unknown_event_type_is_skipped(
    server_and_port: tuple[RemoteControlServer, int],
    callback: MagicMock,
) -> None:
    _, port = server_and_port
    await _send_lines(port, [
        json.dumps({"control_key": "SOUTH_BUTTON", "event": "INVALID_TYPE"}),
    ])

    callback.assert_not_called()


@pytest.mark.asyncio
async def test_missing_fields_are_skipped(
    server_and_port: tuple[RemoteControlServer, int],
    callback: MagicMock,
) -> None:
    _, port = server_and_port
    await _send_lines(port, [
        json.dumps({"control_key": "SOUTH_BUTTON"}),  # missing event
        json.dumps({"event": "ON"}),  # missing control_key
    ])

    callback.assert_not_called()


@pytest.mark.asyncio
async def test_empty_lines_are_ignored(
    server_and_port: tuple[RemoteControlServer, int],
    callback: MagicMock,
) -> None:
    _, port = server_and_port
    await _send_lines(port, [
        "",
        json.dumps({"control_key": "SOUTH_BUTTON", "event": "ON"}),
        "",
    ])

    callback.assert_called_once()
