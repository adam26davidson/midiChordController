#!/usr/bin/env python3
"""MCP server exposing Pi deployment, remote control, and screenshot tools."""

from __future__ import annotations

import base64
import os
import subprocess

from mcp.server.fastmcp import FastMCP

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
DEPLOY_DIR = os.path.join(TOOLS_DIR, "deploy")
TEST_DIR = os.path.join(TOOLS_DIR, "test")
PROJECT_DIR = os.path.dirname(TOOLS_DIR)

mcp = FastMCP("pi-tools")


def _run(script: str, *args: str, timeout: int = 15, script_dir: str = TOOLS_DIR) -> str:
    """Run a shell script and return its output."""
    cmd = [os.path.join(script_dir, script), *args]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        output = (result.stdout + result.stderr).strip()
        return output if output else "(no output)"
    except subprocess.TimeoutExpired:
        return f"Error: {script} timed out after {timeout}s"
    except FileNotFoundError:
        return f"Error: {script} not found in {script_dir}"


def _deploy(script: str, *args: str, timeout: int = 15) -> str:
    """Run a deploy script from tools/deploy/."""
    return _run(script, *args, timeout=timeout, script_dir=DEPLOY_DIR)


def _test(script: str, *args: str, timeout: int = 15) -> str:
    """Run a test script from tools/test/."""
    return _run(script, *args, timeout=timeout, script_dir=TEST_DIR)


# ---------------------------------------------------------------------------
# High-level tools
# ---------------------------------------------------------------------------


@mcp.tool()
def pi_ping() -> str:
    """Check if the Pi is reachable via SSH. Use this to verify connectivity before other operations."""
    return _deploy("pi.sh", "ping")


@mcp.tool()
def pi_up() -> str:
    """One-shot sync code to Pi and start the app. No daemons — safe for automated testing."""
    return _deploy("pi.sh", "up", timeout=30)


@mcp.tool()
def pi_down() -> str:
    """Stop everything: stop the app on Pi, then stop sync and start scripts locally."""
    return _deploy("pi.sh", "down")


@mcp.tool()
def pi_restart() -> str:
    """Restart the app: stop app, one-shot re-sync, start app. No daemons."""
    return _deploy("pi.sh", "restart", timeout=30)


@mcp.tool()
def pi_status() -> str:
    """Check status of everything: local sync/start scripts and the app on the Pi."""
    return _deploy("pi.sh", "status")


@mcp.tool()
def pi_logs(source: str = "start", lines: int = 50) -> str:
    """View recent logs from the app or scripts.

    Args:
        source: "start" (app stdout/stderr, default) or "sync" (sync log)
        lines: Number of lines to show (default 50)
    """
    return _deploy("pi.sh", "logs", source, str(lines))


@mcp.tool()
def pi_screenshot() -> list[dict[str, str]]:
    """Take a screenshot of the Pi's display and return it as an image."""
    output_path = "/tmp/pi_mcp_screenshot.png"
    result = _test("pi_screenshot.sh", output_path)
    if not os.path.exists(output_path):
        return [{"type": "text", "text": f"Screenshot failed: {result}"}]
    with open(output_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()
    return [
        {"type": "text", "text": result},
        {"type": "image", "data": image_data, "mimeType": "image/png"},
    ]


@mcp.tool()
def pi_record(frames: int = 10, interval: int = 100) -> list[dict[str, str]]:
    """Capture a sequence of screenshots to observe animations or state transitions.
    Returns a grid image stitching all frames together for quick review.

    Args:
        frames: Number of frames to capture (default: 10, max: 20)
        interval: Minimum ms between frames (default: 100, 0 = as fast as possible ~10fps)
    """
    import shutil

    frames = min(frames, 20)
    output_dir = "/tmp/pi_mcp_recording"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    result = _test("pi_record.sh", "--frames", str(frames), "--interval", str(interval), "--output", output_dir, timeout=30)

    items: list[dict[str, str]] = [{"type": "text", "text": result}]

    # Return the grid image if available
    grid_path = os.path.join(output_dir, "grid.png")
    if os.path.exists(grid_path):
        with open(grid_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode()
        items.append({"type": "image", "data": image_data, "mimeType": "image/png"})
    return items


@mcp.tool()
def pi_send_and_screenshot(
    control_key: str,
    action: str = "press",
    value: float | None = None,
    duration: int = 100,
) -> list[dict[str, str]]:
    """Send a controller event and immediately take a screenshot to see the result.

    Args:
        control_key: The control to activate (e.g. SOUTH_BUTTON, GYRO_PITCH, WEST_BUTTON)
        action: "press" (ON+delay+OFF), "on", "off", or "analog"
        value: Float value for analog events (-1.0 to 1.0)
        duration: Hold duration in ms for press action (default 100)
    """
    if action == "press":
        event_result = _test("pi_send_event.sh", "press", control_key, "--duration", str(duration))
    elif action == "on":
        event_result = _test("pi_send_event.sh", "event", control_key, "ON")
    elif action == "off":
        event_result = _test("pi_send_event.sh", "event", control_key, "OFF")
    elif action == "analog":
        if value is None:
            return [{"type": "text", "text": "Error: value is required for analog action"}]
        event_result = _test("pi_send_event.sh", "analog", control_key, str(value))
    else:
        return [{"type": "text", "text": f"Unknown action: {action}. Use press, on, off, or analog."}]

    import time
    time.sleep(0.2)
    screenshot = pi_screenshot()

    event_msg = f"Sent: {action} {control_key}" + (f" {value}" if value is not None else "") + (f"\n{event_result}" if event_result != "(no output)" else "")
    return [{"type": "text", "text": event_msg}, *screenshot]


# ---------------------------------------------------------------------------
# Low-level tools
# ---------------------------------------------------------------------------


@mcp.tool()
def pi_send_event(
    control_key: str,
    event_type: str,
    value: float | None = None,
) -> str:
    """Send a single raw controller event to the app on the Pi.

    Args:
        control_key: Control key (e.g. SOUTH_BUTTON, GYRO_PITCH, RIGHT_BUMPER)
        event_type: Event type: ON, OFF, POSITIVE, NEGATIVE, UPDATE
        value: Float value for UPDATE events (-1.0 to 1.0)
    """
    args = ["event", control_key, event_type]
    if value is not None:
        args.append(str(value))
    return _test("pi_send_event.sh", *args)


@mcp.tool()
def pi_press(control_key: str, duration: int = 100) -> str:
    """Simulate a button press (ON + delay + OFF).

    Args:
        control_key: Button to press (e.g. SOUTH_BUTTON, WEST_BUTTON, RIGHT_BUMPER)
        duration: Hold duration in ms (default 100)
    """
    return _test("pi_send_event.sh", "press", control_key, "--duration", str(duration))


@mcp.tool()
def pi_analog(control_key: str, value: float) -> str:
    """Send an analog UPDATE event.

    Args:
        control_key: Analog control (e.g. GYRO_PITCH, RIGHT_STICK_X_POLAR, LEFT_STICK_Y_POLAR)
        value: Analog value (-1.0 to 1.0)
    """
    return _test("pi_send_event.sh", "analog", control_key, str(value))


@mcp.tool()
def pi_reset() -> str:
    """Reset all controller state: release all buttons and zero all analog controls. Use this at the start of a session or when state might be stale from a previous session."""
    return _test("pi_send_event.sh", "reset")


@mcp.tool()
def pi_midi_history(
    count: int = 50,
    types: str | None = None,
) -> str:
    """Query recent MIDI output messages from the app.

    Args:
        count: Max number of events to return (default 50)
        types: Comma-separated filter of event types to include.
               Options: note_on, note_off, aftertouch, poly_aftertouch, control_change.
               Default: all types.
    """
    args = ["midi", "--count", str(count)]
    if types:
        args.extend(["--types", types])
    return _test("pi_send_event.sh", *args)


@mcp.tool()
def pi_midi_in(
    note: int,
    midi_type: str = "note_on",
    velocity: int = 100,
    channel: int = 0,
) -> str:
    """Send MIDI input to the app (for external chord engine).

    Args:
        note: MIDI note number (0-127, e.g. 60=C4, 64=E4, 67=G4)
        midi_type: "note_on" or "note_off" (default: note_on)
        velocity: Velocity for note_on (default: 100)
        channel: MIDI channel (default: 0)
    """
    args = ["midi_in", midi_type, str(note), str(velocity), "--channel", str(channel)]
    return _test("pi_send_event.sh", *args)


@mcp.tool()
def pi_touch(
    x: int,
    y: int,
    to_x: int | None = None,
    to_y: int | None = None,
    steps: int = 10,
    duration: int = 200,
) -> list[dict[str, str]]:
    """Simulate a touch gesture on the Pi's display and return an annotated screenshot.
    The screenshot shows the result with the gesture path overlaid (red line/crosshair).

    Args:
        x: X coordinate (tap location, or drag start)
        y: Y coordinate (tap location, or drag start)
        to_x: End X for drag gesture (omit for tap)
        to_y: End Y for drag gesture (omit for tap)
        steps: Interpolation steps for drag (default: 10)
        duration: Drag duration in ms (default: 200)
    """
    if to_x is not None and to_y is not None:
        result = _test("pi_touch.sh", "--from", f"{x},{y}", "--to", f"{to_x},{to_y}",
                       "--steps", str(steps), "--duration", str(duration))
    else:
        result = _test("pi_touch.sh", "--tap", f"{x},{y}")

    # Find the output file
    import glob
    files = sorted(glob.glob("/tmp/pi_touch_*.png"))
    # Filter out raw screenshots
    files = [f for f in files if "raw" not in f]
    if not files:
        return [{"type": "text", "text": f"Touch failed: {result}"}]

    latest = files[-1]
    with open(latest, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()
    return [
        {"type": "text", "text": result},
        {"type": "image", "data": image_data, "mimeType": "image/png"},
    ]


@mcp.tool()
def pi_sequence(steps_json: str) -> list[dict[str, str]]:
    """Run a sequence of controller events, screenshots, recordings, and MIDI queries in one call.

    Accepts a JSON array of steps. Each step is one of:
      {"event": "SOUTH_BUTTON ON"}         - Send raw event
      {"press": "SOUTH_BUTTON"}            - Press + release (optional "duration": ms)
      {"analog": "GYRO_PITCH 0.5"}        - Analog update
      {"midi_in": "note_on 60 100"}       - MIDI input
      {"delay": 200}                       - Delay in ms
      {"screenshot": "label"}             - Take labeled screenshot
      {"record": {"frames": 6}}           - Record frame grid
      {"midi": {"types": ["note_on"]}}    - Query MIDI history
      {"reset": true}                      - Reset all controls
      {"touch_tap": "400,240"}            - Tap at coordinates
      {"touch_drag": {"from": "200,300", "to": "600,100"}}

    Example: '[{"reset": true}, {"press": "SOUTH_BUTTON"}, {"delay": 200}, {"screenshot": "after_press"}, {"midi": {"types": ["note_on", "note_off"]}}]'

    Args:
        steps_json: JSON array of sequence steps
    """
    import json as _json
    import shutil

    data = _json.loads(steps_json)
    # Support both flat array and object with "steps" key
    steps = data["steps"] if isinstance(data, dict) else data
    output_dir = "/tmp/pi_mcp_sequence"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    # Import and run
    import importlib.util
    spec = importlib.util.spec_from_file_location("run_sequence", os.path.join(TEST_DIR, "run_sequence.py"))
    assert spec is not None
    assert spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    raw_results = mod.run_sequence(steps, output_dir)

    # Convert to MCP response
    items: list[dict[str, str]] = []
    for r in raw_results:
        if r["type"] == "text":
            items.append({"type": "text", "text": r["text"]})
        elif r["type"] == "midi":
            items.append({"type": "text", "text": r["data"]})
        elif r["type"] == "image_path":
            path = r["path"]
            if os.path.exists(path):
                with open(path, "rb") as f:
                    image_data = base64.b64encode(f.read()).decode()
                items.append({"type": "text", "text": r.get("label", "image")})
                items.append({"type": "image", "data": image_data, "mimeType": "image/png"})
    return items


if __name__ == "__main__":
    mcp.run(transport="stdio")
