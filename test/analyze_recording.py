"""Summarize an evdev recording: event rates, button timings, and density.

Parses a .jsonl evdev recording and reports per-device event rates, button
press/release timings with hold durations, orphan detection, and event
density distribution across 10ms windows. Useful for understanding
controller behavior before tuning processing parameters.

Usage:
    python test/analyze_recording.py [path/to/recording.jsonl]
"""
import json
import sys
from collections import defaultdict
from pathlib import Path


def analyze(path):
    events_by_device = defaultdict(lambda: defaultdict(list))  # device -> type -> [timestamps]
    button_events = []  # (timestamp, device, code, value)
    first_t: "float | None" = None
    last_t: "float | None" = None
    count = 0

    with open(path) as f:
        for line in f:
            data = json.loads(line)
            t = data["t"]
            if first_t is None:
                first_t = t
            last_t = t
            count += 1

            events_by_device[data["device"]][data["type"]].append(t)

            if data["type"] == 1:
                button_events.append((t, data["device"], data["code"], data["value"]))

    assert last_t is not None and first_t is not None
    duration = last_t - first_t
    print(f"Recording: {count} events over {duration:.2f}s\n")

    # Event rates by device and type
    type_names = {1: "EV_KEY (button/pad)", 3: "EV_ABS (analog)", 4: "EV_MSC (misc)"}

    print("=== Event rates by device ===")
    for device in sorted(events_by_device.keys()):
        types = events_by_device[device]
        total = sum(len(ts) for ts in types.values())
        print(f"\n  {device}: {total} events ({total/duration:.0f}/sec)")
        for etype in sorted(types.keys()):
            ts = types[etype]
            name = type_names.get(etype, f"type={etype}")
            print(f"    {name}: {len(ts)} ({len(ts)/duration:.0f}/sec)")

            # Show inter-event timing stats
            if len(ts) > 1:
                gaps = [ts[i+1] - ts[i] for i in range(len(ts)-1)]
                gaps.sort()
                avg = sum(gaps) / len(gaps)
                p50 = gaps[len(gaps)//2]
                p99 = gaps[int(len(gaps)*0.99)]
                max_gap = gaps[-1]
                print(f"      gap: avg={avg*1000:.1f}ms  p50={p50*1000:.1f}ms  p99={p99*1000:.1f}ms  max={max_gap*1000:.1f}ms")

    # Button event details
    print(f"\n=== Button events ({len(button_events)}) ===")
    pressed = {}  # code -> press_timestamp
    durations = []
    for t, device, code, value in button_events:
        if value == 1:
            pressed[code] = t
            print(f"  {t - first_t:8.3f}s  {device}  code={code}  PRESS")
        elif value == 0:
            dur = ""
            if code in pressed:
                d = t - pressed[code]
                durations.append(d)
                dur = f"  (held {d*1000:.0f}ms)"
                del pressed[code]
            else:
                dur = "  (ORPHAN - no matching press!)"
            print(f"  {t - first_t:8.3f}s  {device}  code={code}  RELEASE{dur}")
        elif value == 2:
            print(f"  {t - first_t:8.3f}s  {device}  code={code}  REPEAT")

    if pressed:
        print(f"\n  WARNING: {len(pressed)} buttons still pressed at end of recording:")
        for code, t in pressed.items():
            print(f"    code={code} pressed at {t - first_t:.3f}s (MISSING RELEASE)")

    if durations:
        print(f"\n  Hold duration stats: min={min(durations)*1000:.0f}ms  avg={sum(durations)/len(durations)*1000:.0f}ms  max={max(durations)*1000:.0f}ms")

    # Check for bursts: how many events in each 10ms window
    print("\n=== Event density (10ms windows) ===")
    all_timestamps = []
    for device in events_by_device:
        for etype in events_by_device[device]:
            all_timestamps.extend(events_by_device[device][etype])
    all_timestamps.sort()

    window = 0.01
    window_counts = []
    i = 0
    while i < len(all_timestamps):
        j = i
        while j < len(all_timestamps) and all_timestamps[j] - all_timestamps[i] < window:
            j += 1
        window_counts.append(j - i)
        i = j

    if window_counts:
        window_counts.sort()
        print(f"  Windows: {len(window_counts)}")
        print(f"  Events per 10ms: avg={sum(window_counts)/len(window_counts):.1f}  p50={window_counts[len(window_counts)//2]}  p95={window_counts[int(len(window_counts)*0.95)]}  p99={window_counts[int(len(window_counts)*0.99)]}  max={window_counts[-1]}")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent / "evdev_recording.jsonl"
    analyze(path)
