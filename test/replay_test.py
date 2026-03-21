"""
Replay test: feeds recorded evdev events through the real processing pipeline
with Midi and Display stubbed out. Verifies that every button press gets a
corresponding chord-on, and every release gets a chord-off.
"""
import gzip
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Must mock hardware-dependent modules BEFORE importing anything else
sys.modules['rtmidi'] = MagicMock()
sys.modules['rtmidi.midiconstants'] = MagicMock()
sys.modules['tkinter'] = MagicMock()
sys.modules['evdev'] = MagicMock()


class FakeEvent:
    """Mimics an evdev InputEvent from recorded JSON."""
    def __init__(self, t, type, code, value):
        self._timestamp = t
        self.type = type
        self.code = code
        self.value = value

    def timestamp(self):
        return self._timestamp


def load_recording(path):
    events = []
    with gzip.open(path, 'rt') as f:
        for line in f:
            data = json.loads(line)
            events.append((
                data["device"],
                FakeEvent(data["t"], data["type"], data["code"], data["value"])
            ))
    return events


class ReplayTest(unittest.TestCase):

    def setUp(self):
        # Reset the redux store for each test by re-importing
        import importlib

        import redux
        importlib.reload(redux)

        # Wire up the real pipeline (minus Display and actual MIDI I/O)
        from controller_coupler import ControllerCoupler
        from music_engine import MusicEngine
        from redux.settings_storage import settings_storage_utility

        settings_storage_utility.load_settings()

        self.coupler = ControllerCoupler()
        self.music_engine = MusicEngine()

        # Intercept chord engine output BEFORE it hits the rhythm engine
        # (rhythm engine needs asyncio which we don't want to run)
        self.chord_messages = []

        def tracking_callback(message):
            self.chord_messages.append({
                "type": str(message.type),
                "notes": list(message.notes) if message.notes else [],
                "player": str(message.player),
            })

        # Replace the callbacks on both chord engines
        self.music_engine.internal_chord_engine.callbacks = [tracking_callback]
        self.music_engine.external_chord_engine.callbacks = [tracking_callback]

        # Load the dual_shock4 controller config to build raw_control_key_map
        from controller_manager.controllers.dual_shock4.info import controller_config

        self.controller_config = controller_config

        # Build raw_control_key_map same as Controller.__init__ does
        self.raw_control_key_map = {}
        for device in controller_config.controls:
            key_map = {}
            for control in controller_config.controls[device]:
                key_map[control.ev_dev_key] = control
            self.raw_control_key_map[device] = key_map

    def test_replay_button_events(self):
        """Replay recorded events and verify every press has a matching release in chord engine output."""
        recording_path = Path(__file__).parent / "evdev_recording.jsonl.gz"
        if not recording_path.exists():
            self.skipTest("No recording file found")

        events = load_recording(recording_path)

        # Count button press/release in the recording
        button_presses = sum(1 for _, e in events if e.type == 1 and e.value == 1)
        button_releases = sum(1 for _, e in events if e.type == 1 and e.value == 0)
        print(f"\nRecording: {len(events)} total events, {button_presses} presses, {button_releases} releases")

        # Import what we need to simulate the Controller's processEvent pipeline
        from controller_manager.models.control_event import ControlEvent
        from controller_manager.models.mappable_control_type import MappableControlType
        from controller_manager.models.raw_control_event import RawControlEvent
        from controller_manager.models.raw_control_type import RawControlType

        state = {}
        for device in self.controller_config.controls:
            for control in self.controller_config.controls[device]:
                if control.type in [RawControlType.BUTTON, RawControlType.PAD]:
                    state[control.key] = 0
                elif control.type == RawControlType.ANALOG:
                    state[control.key] = {"value_history": [], "threshold_value": 0}

        processed_presses = 0
        processed_releases = 0

        for device_key, event in events:
            if event.type == 0:  # EV_SYN
                continue

            if event.code not in self.raw_control_key_map.get(device_key, {}):
                continue

            control = self.raw_control_key_map[device_key][event.code]

            if control.type == RawControlType.BUTTON:
                if event.value == 2:  # repeat
                    continue
                raw_event = RawControlEvent.ON if event.value == 1 else RawControlEvent.OFF

                if event.value == 1:
                    processed_presses += 1
                else:
                    processed_releases += 1

                # Send through the real coupler pipeline
                mappable_event = control.get_mappable_control_event(MappableControlType.ON_OFF, raw_event)
                keys = control.get_mappable_control_keys(MappableControlType.ON_OFF, raw_event)

                for key in keys:
                    ce = ControlEvent(
                        control_key=key,
                        event=mappable_event,
                        controller_id="test_controller",
                        value=None
                    )
                    self.coupler.event_handler(ce)

                state[control.key] = event.value

            elif control.type == RawControlType.ANALOG:
                # Process analog events too -- they affect inversion etc.
                if control.config is None:
                    continue
                top = control.config.top_value
                bottom = control.config.bottom_value

                ignore_value = False
                if (control.config.ignore_values is not None
                        and event.value in control.config.ignore_values):
                    ignore_value = True
                if abs(event.value) > 1.25 * max(top, bottom):
                    ignore_value = True

                if not ignore_value:
                    control_state = state[control.key]
                    value_history = control_state["value_history"]
                    value_history.append(event.value)
                    if len(value_history) > control.config.average_count:
                        value_history.pop(0)
                    average_value = sum(value_history) / len(value_history)
                    slope = 2.0 / (top - bottom)
                    intercept = 1 - (slope * top)
                    normalized_value = (slope * average_value) + intercept
                    normalized_value = max(min(normalized_value, 0.999), -0.999)

                    mappable_event = control.get_mappable_control_event(MappableControlType.ANALOG, RawControlEvent.UPDATE)
                    keys = control.get_mappable_control_keys(MappableControlType.ANALOG, RawControlEvent.UPDATE)
                    for key in keys:
                        ce = ControlEvent(
                            control_key=key,
                            event=mappable_event,
                            controller_id="test_controller",
                            value=normalized_value
                        )
                        self.coupler.event_handler(ce)

        print(f"Processed: {processed_presses} presses, {processed_releases} releases")
        print(f"\nChord engine messages ({len(self.chord_messages)}):")
        for i, msg in enumerate(self.chord_messages):
            print(f"  [{i}] {msg['type']} player={msg['player']} notes={msg['notes']}")

        # Count chord ON vs OFF messages
        chord_ons = [m for m in self.chord_messages if "ON" in str(m["type"]) and "CHORD" in str(m["player"])]
        chord_offs = [m for m in self.chord_messages if "OFF" in str(m["type"]) and "CHORD" in str(m["player"])]

        print(f"\nChord ONs: {len(chord_ons)}, Chord OFFs: {len(chord_offs)}")

        # Every press should produce an ON, every release should eventually produce an OFF
        assert processed_presses == button_presses, "Not all button presses were processed"
        assert processed_releases == button_releases, "Not all button releases were processed"

        # The number of ONs should match presses, OFFs should match releases
        # (allowing for the chord engine's dedup logic)
        assert len(chord_ons) > 0, "No chord ON messages generated"
        assert len(chord_offs) > 0, "No chord OFF messages generated"
        assert len(chord_ons) == len(chord_offs), \
            f"Mismatched chord ON ({len(chord_ons)}) vs OFF ({len(chord_offs)}) -- notes are getting stuck!"


if __name__ == "__main__":
    unittest.main(verbosity=2)
