"""Analyze how often the gyro-driven inversion value actually changes.

Simulates the gyro → normalized value → snapped inversion pipeline offline
against a recorded evdev session to measure the real change rate. Useful for
tuning INVERSION_SNAP and the centered_threshold to reduce unnecessary
chord-engine updates.

Usage:
    python test/analyze_inversion_changes.py [path/to/recording.jsonl]
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.modules['rtmidi'] = type(sys)('rtmidi')
sys.modules['rtmidi.midiconstants'] = type(sys)('rtmidi.midiconstants')
sys.modules['tkinter'] = type(sys)('tkinter')
sys.modules['evdev'] = type(sys)('evdev')

rtmidi = sys.modules['rtmidi']
rtmidi.MidiOut = lambda: type('MidiOut', (), {'get_ports': lambda s: [], 'send_message': lambda s,m: None})()  # type: ignore[attr-defined]
rtmidi.MidiIn = lambda: type('MidiIn', (), {'get_ports': lambda s: [], 'set_callback': lambda s,c,d=None: None})()  # type: ignore[attr-defined]

from constants import INVERSION_SNAP

path = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent / "evdev_recording.jsonl")

# Simulate gyro -> inversion processing
# GYRO_PITCH is evDevKey=2 on motion device, mapped to INTERNAL_INVERSION
# From info.py: topValue=-8050, bottomValue=8050, centeredThreshold=0.6

inversion_range = 3  # default range
inversion_value = 0
call_count = 0
change_count = 0
first_t = None

def process_value(raw_value, max_steps, last_value):
    def get_value(x):
        return math.floor(((x+1)/2)*((2*max_steps)+1)) - max_steps
    value = get_value(raw_value)
    snap = (1.0 / (max_steps + 1)) * INVERSION_SNAP
    if value == last_value + 1:
        raw_value -= snap
        value = get_value(raw_value)
    if value == last_value - 1:
        raw_value += snap
        value = get_value(raw_value)
    return value

with open(path) as f:
    for line in f:
        data = json.loads(line)
        if first_t is None:
            first_t = data["t"]
        if data["t"] - first_t > 5.0:
            break

        # GYRO_PITCH: device=motion, type=3, code=2
        if data["device"] == "motion" and data["type"] == 3 and data["code"] == 2:
            value = data["value"]
            # Normalize (same as processAnalogEvent)
            top = -8050
            bottom = 8050
            if value == 0:
                continue  # ignoreValues=[0]
            if abs(value) > 1.25 * max(top, bottom):
                continue
            slope = 2.0 / (top - bottom)
            intercept = 1 - (slope * top)
            nv = max(min((slope * value) + intercept, 0.999), -0.999)

            new_inversion = process_value(nv, inversion_range, inversion_value)
            call_count += 1
            if new_inversion != inversion_value:
                change_count += 1
                print(f"  t={data['t']-first_t:.3f}s  gyro={value}  normalized={nv:.3f}  inversion: {inversion_value} -> {new_inversion}")
                inversion_value = new_inversion

print(f"\nGyro samples processed: {call_count}")
print(f"Inversion value changes: {change_count}")
print(f"Change rate: {change_count}/{call_count} = {change_count/max(call_count,1)*100:.1f}%")
print(f"Expensive updateChordEngine calls/sec: {change_count/5:.1f}")
