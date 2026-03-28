#!/usr/bin/env python3
"""Run a sequence of controller events, screenshots, recordings, and MIDI queries.

Accepts a JSON sequence either as a file path or inline string.

Sequence format - list of steps:
  {"event": "SOUTH_BUTTON ON"}           # Send raw event (key + event_type)
  {"event": "SOUTH_BUTTON ON", "value": 0.5}  # Event with value
  {"press": "SOUTH_BUTTON"}              # Press + release (ON, delay, OFF)
  {"press": "SOUTH_BUTTON", "duration": 200}   # Custom hold duration
  {"analog": "GYRO_PITCH 0.5"}          # Analog update
  {"midi_in": "note_on 60 100"}         # MIDI input
  {"delay": 200}                         # Delay in ms
  {"screenshot": "label"}               # Take screenshot with label
  {"record": {"frames": 6, "interval": 80}}  # Record frame sequence (grid)
  {"midi": {"types": ["note_on"]}}      # Query MIDI history
  {"midi": {"count": 10}}               # Query with count
  {"reset": true}                        # Reset all controls
  {"touch_tap": "400,240"}              # Tap at coordinates
  {"touch_drag": {"from": "200,300", "to": "600,100"}}  # Drag gesture

Usage:
  python3 tools/test/run_sequence.py sequence.json --host chord-controller
  python3 tools/test/run_sequence.py '[{"press": "SOUTH_BUTTON"}, {"delay": 200}, {"screenshot": "after"}]'
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import time

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))


def _run(script: str, *args: str, timeout: int = 30) -> str:
    cmd = [os.path.join(TOOLS_DIR, script), *args]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return (result.stdout + result.stderr).strip()
    except subprocess.TimeoutExpired:
        return f"TIMEOUT: {script}"


def _send_event(host: str, port: int, *args: str) -> str:
    cmd = [sys.executable, os.path.join(TOOLS_DIR, "send_event.py"), "--host", host, "--port", str(port), *args]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return (result.stdout + result.stderr).strip()
    except subprocess.TimeoutExpired:
        return "TIMEOUT"


def run_sequence(
    steps: list[dict[str, object]],
    output_dir: str,
    host: str = "chord-controller",
    port: int = 9999,
) -> list[dict[str, str]]:
    """Execute a sequence of steps and collect results."""
    os.makedirs(output_dir, exist_ok=True)
    results: list[dict[str, str]] = []
    screenshot_count = 0
    record_count = 0

    for i, step in enumerate(steps):
        step_num = i + 1

        if "delay" in step:
            ms = int(step["delay"])  # type: ignore[arg-type]
            time.sleep(ms / 1000.0)

        elif "event" in step:
            parts = str(step["event"]).split()
            args = ["event", parts[0], parts[1]]
            if "value" in step:
                args.append(str(step["value"]))
            result = _send_event(host, port, *args)
            if result:
                results.append({"type": "text", "text": f"Step {step_num}: event {step['event']} → {result}"})

        elif "press" in step:
            args = ["press", str(step["press"])]
            if "duration" in step:
                args.extend(["--duration", str(step["duration"])])
            _send_event(host, port, *args)

        elif "analog" in step:
            parts = str(step["analog"]).split()
            _send_event(host, port, "analog", parts[0], parts[1])

        elif "midi_in" in step:
            parts = str(step["midi_in"]).split()
            _send_event(host, port, "midi_in", *parts)

        elif "reset" in step:
            _send_event(host, port, "reset")

        elif "screenshot" in step:
            screenshot_count += 1
            label = str(step["screenshot"]) if step["screenshot"] is not True else f"screenshot_{screenshot_count}"
            filename = f"{screenshot_count:02d}_{label}.png"
            filepath = os.path.join(output_dir, filename)
            time.sleep(0.15)
            _run("pi_screenshot.sh", filepath)
            results.append({"type": "text", "text": f"Step {step_num}: screenshot '{label}'"})
            if os.path.exists(filepath):
                results.append({"type": "image_path", "path": filepath, "label": label})

        elif "record" in step:
            record_count += 1
            opts = step["record"] if isinstance(step["record"], dict) else {}
            frames = str(opts.get("frames", 8))  # type: ignore[union-attr]
            interval = str(opts.get("interval", 100))  # type: ignore[union-attr]
            record_dir = os.path.join(output_dir, f"recording_{record_count:02d}")
            result = _run("pi_record.sh", "--frames", frames, "--interval", interval, "--output", record_dir)
            results.append({"type": "text", "text": f"Step {step_num}: record {frames} frames → {result}"})
            grid_path = os.path.join(record_dir, "grid.png")
            if os.path.exists(grid_path):
                results.append({"type": "image_path", "path": grid_path, "label": f"recording_{record_count}"})

        elif "midi" in step:
            opts = step["midi"] if isinstance(step["midi"], dict) else {}
            args = ["midi"]
            if "count" in opts:  # type: ignore[operator]
                args.extend(["--count", str(opts["count"])])  # type: ignore[index]
            if "types" in opts:  # type: ignore[operator]
                args.extend(["--types", ",".join(opts["types"])])  # type: ignore[index]
            result = _send_event(host, port, *args)
            results.append({"type": "text", "text": f"Step {step_num}: midi query"})
            results.append({"type": "midi", "data": result})

        elif "touch_tap" in step:
            coords = str(step["touch_tap"])
            filepath = os.path.join(output_dir, f"touch_tap_{step_num:02d}.png")
            result = _run("pi_touch.sh", "--tap", coords)
            # Find and copy the latest touch output
            touch_files = sorted(f for f in glob.glob("/tmp/pi_touch_*.png") if "raw" not in f)
            if touch_files:
                shutil.copy2(touch_files[-1], filepath)
            results.append({"type": "text", "text": f"Step {step_num}: tap {coords}"})
            if os.path.exists(filepath):
                results.append({"type": "image_path", "path": filepath, "label": f"tap_{coords}"})

        elif "touch_drag" in step:
            opts = step["touch_drag"]
            from_coords = str(opts["from"])  # type: ignore[index]
            to_coords = str(opts["to"])  # type: ignore[index]
            filepath = os.path.join(output_dir, f"touch_drag_{step_num:02d}.png")
            result = _run("pi_touch.sh", "--from", from_coords, "--to", to_coords)
            touch_files = sorted(f for f in glob.glob("/tmp/pi_touch_*.png") if "raw" not in f)
            if touch_files:
                shutil.copy2(touch_files[-1], filepath)
            results.append({"type": "text", "text": f"Step {step_num}: drag {from_coords} → {to_coords}"})
            if os.path.exists(filepath):
                results.append({"type": "image_path", "path": filepath, "label": f"drag_{from_coords}_{to_coords}"})

        else:
            results.append({"type": "text", "text": f"Step {step_num}: unknown step type: {step}"})

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a test sequence")
    parser.add_argument("sequence", help="JSON file path or inline JSON string")
    parser.add_argument("--host", default="chord-controller")
    parser.add_argument("--port", type=int, default=9999)
    parser.add_argument("--output", "-o", default=None)
    args = parser.parse_args()

    # Parse sequence from file or inline
    seq_input = args.sequence
    if os.path.isfile(seq_input):
        with open(seq_input) as f:
            data = json.load(f)
    else:
        data = json.loads(seq_input)

    # Support both flat array and object with "steps" key
    if isinstance(data, dict):
        test_name = data.get("name", "unnamed")
        steps = data["steps"]
        print(f"Test: {test_name}")
        if "description" in data:
            print(f"  {data['description']}")
        print()
    else:
        steps = data
        test_name = "inline"

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_dir = args.output or f"/tmp/pi_sequence_{timestamp}"

    results = run_sequence(steps, output_dir, args.host, args.port)

    for r in results:
        if r["type"] == "text":
            print(r["text"])
        elif r["type"] == "midi":
            print(r["data"])
        elif r["type"] == "image_path":
            print(f"  → {r['path']}")

    print(f"\nResults saved to {output_dir}")


if __name__ == "__main__":
    main()
