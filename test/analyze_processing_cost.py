"""Measure coupler throughput: which events trigger actions vs get dropped.

Replays a recorded evdev session through the real ControllerCoupler pipeline
(with hardware stubs) and counts how many events reach each AppParameter vs
get filtered out by engine mode, missing mappings, etc. Reports per-second
rates for both executed and dropped events.

Usage:
    python test/analyze_processing_cost.py [path/to/recording.jsonl]
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.modules['rtmidi'] = type(sys)('rtmidi')
sys.modules['rtmidi.midiconstants'] = type(sys)('rtmidi.midiconstants')
sys.modules['tkinter'] = type(sys)('tkinter')
sys.modules['evdev'] = type(sys)('evdev')

# Stub out rtmidi classes
import sys as _sys

rtmidi = _sys.modules['rtmidi']
rtmidi.MidiOut = lambda: type('MidiOut', (), {'get_ports': lambda self: [], 'open_port': lambda self, p: None, 'send_message': lambda self, m: None})()
rtmidi.MidiIn = lambda: type('MidiIn', (), {'get_ports': lambda self: [], 'set_callback': lambda self, cb, data=None: None, 'open_port': lambda self, p: None})()

from controller_coupler import ControllerCoupler
from controller_manager.controllers.dual_shock4.info import controller_config
from controller_manager.models.control_event import ControlEvent
from controller_manager.models.mappable_control_type import MappableControlType
from controller_manager.models.raw_control_event import RawControlEvent
from controller_manager.models.raw_control_type import RawControlType
from music_engine import MusicEngine
from redux.settings_storage import settings_storage_utility

settings_storage_utility.load_settings()
coupler = ControllerCoupler()
me = MusicEngine()

# Patch coupler to count actions
exec_count = defaultdict(int)
drop_count = defaultdict(int)
original_handler = coupler.event_handler

def counting_handler(event):
    if event.control_key in coupler.map.map:
        parameter_keys = coupler.map.map[event.control_key]
        for parameter_key in parameter_keys:
            if parameter_key in coupler.parameters:
                parameter = coupler.parameters[parameter_key]
                if coupler._ControllerCoupler__use_parameter(parameter):
                    command = coupler._ControllerCoupler__map_control_event_to_parameter_event(event.event, parameter)
                    if command in parameter.command_mappings:
                        exec_count[parameter_key] += 1
                    else:
                        drop_count[f"{parameter_key} (no cmd mapping)"] += 1
                else:
                    drop_count[f"{parameter_key} (wrong engine mode)"] += 1
            else:
                drop_count[f"{parameter_key} (not in params)"] += 1
    else:
        drop_count[f"{event.control_key} (not in map)"] += 1

# Build control key map
raw_control_key_map = {}
for device in controller_config.controls:
    key_map = {}
    for control in controller_config.controls[device]:
        key_map[control.ev_dev_key] = control
    raw_control_key_map[device] = key_map

# Build analog state
analog_state = {}
for device in controller_config.controls:
    for control in controller_config.controls[device]:
        if control.type == RawControlType.ANALOG:
            analog_state[control.key] = {"value_history": [], "threshold_value": 0}

path = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent / "evdev_recording.jsonl")

# Only process first 5 seconds
events = []
first_t = None
with open(path) as f:
    for line in f:
        data = json.loads(line)
        if first_t is None:
            first_t = data["t"]
        if data["t"] - first_t > 5.0:
            break
        events.append(data)

print(f"Analyzing {len(events)} events (first 5 seconds)")

coupler_calls = 0
for data in events:
    device_key = data["device"]
    etype = data["type"]
    code = data["code"]
    value = data["value"]

    if etype == 0 or code not in raw_control_key_map.get(device_key, {}):
        continue

    control = raw_control_key_map[device_key][code]

    if control.type == RawControlType.BUTTON:
        if value == 2:
            continue
        raw_event = RawControlEvent.ON if value == 1 else RawControlEvent.OFF
        mappable_event = control.get_mappable_control_event(MappableControlType.ON_OFF, raw_event)
        keys = control.get_mappable_control_keys(MappableControlType.ON_OFF, raw_event)
        for key in keys:
            ce = ControlEvent(control_key=key, event=mappable_event, controller_id="test", value=None)
            counting_handler(ce)
            coupler_calls += 1

    elif control.type == RawControlType.ANALOG:
        if control.config is None:
            continue
        top = control.config.top_value
        bottom = control.config.bottom_value
        ignore_value = False
        if control.config.ignore_values and value in control.config.ignore_values:
            ignore_value = True
        if abs(value) > 1.25 * max(top, bottom):
            ignore_value = True
        if not ignore_value:
            cs = analog_state[control.key]
            cs["value_history"].append(value)
            if len(cs["value_history"]) > control.config.average_count:
                cs["value_history"].pop(0)
            avg = sum(cs["value_history"]) / len(cs["value_history"])
            slope = 2.0 / (top - bottom)
            intercept = 1 - (slope * top)
            nv = max(min((slope * avg) + intercept, 0.999), -0.999)

            # ANALOG UPDATE event
            me_analog = control.get_mappable_control_event(MappableControlType.ANALOG, RawControlEvent.UPDATE)
            a_keys = control.get_mappable_control_keys(MappableControlType.ANALOG, RawControlEvent.UPDATE)
            for key in a_keys:
                ce = ControlEvent(control_key=key, event=me_analog, controller_id="test", value=nv)
                counting_handler(ce)
                coupler_calls += 1

            # Threshold events (ON_OFF and POLAR from analog sticks)
            if control.config.centered_threshold is not None:
                threshold_value = 0
                if control.config.threshold is not None:
                    threshold = -1 + (control.config.threshold * 2)
                    if nv > threshold:
                        threshold_value = 1
                else:
                    if nv > control.config.centered_threshold:
                        threshold_value = 1
                    elif nv < -1 * control.config.centered_threshold:
                        threshold_value = -1

                if threshold_value != cs["threshold_value"]:
                    cs["threshold_value"] = threshold_value
                    raw_event = control.config.polar_event_map[threshold_value]
                    if control.config.expose_on_off_events:
                        me_onoff = control.get_mappable_control_event(MappableControlType.ON_OFF, raw_event)
                        oo_keys = control.get_mappable_control_keys(MappableControlType.ON_OFF, raw_event)
                        for key in oo_keys:
                            ce = ControlEvent(control_key=key, event=me_onoff, controller_id="test", value=None)
                            counting_handler(ce)
                            coupler_calls += 1
                    if control.config.expose_polar_events:
                        me_polar = control.get_mappable_control_event(MappableControlType.POLAR, raw_event)
                        p_keys = control.get_mappable_control_keys(MappableControlType.POLAR, raw_event)
                        for key in p_keys:
                            ce = ControlEvent(control_key=key, event=me_polar, controller_id="test", value=None)
                            counting_handler(ce)
                            coupler_calls += 1

print(f"\nTotal coupler calls: {coupler_calls}")
print("\n=== EXECUTED (parameter.command_mappings called) ===")
for key, count in sorted(exec_count.items(), key=lambda x: -x[1]):
    print(f"  {key}: {count} ({count/5:.0f}/sec)")

print("\n=== DROPPED ===")
for key, count in sorted(drop_count.items(), key=lambda x: -x[1]):
    print(f"  {key}: {count} ({count/5:.0f}/sec)")
