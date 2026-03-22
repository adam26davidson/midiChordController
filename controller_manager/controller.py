from __future__ import annotations

import asyncio
import collections
import select
import threading
import time
import traceback
from abc import ABC
from typing import Any, Callable

import evdev
from evdev import InputDevice, InputEvent

from controller_manager.models.control_event import ControlEvent
from redux import get_controller_manager_state, store
from redux.actions import controller_manager as actions

from .maps import me_maps, ui_maps
from .models.controller_config import ControllerConfig
from .models.mappable_control import MappableControl
from .models.mappable_control_type import MappableControlType
from .models.raw_control import RawControl
from .models.raw_control_event import RawControlEvent
from .models.raw_control_type import RawControlType


class Controller(ABC):

    config: ControllerConfig

    def __init__(self, send_event: Callable[[ControlEvent], None], info: object, config: ControllerConfig) -> None:
        self.id: str | None = None
        self.data: dict | None = None
        self.is_connected = False
        self.devices: dict[str, InputDevice] | None = None
        self.send_event = send_event
        self.config = config
        self.info = info
        self.meMap = me_maps[self.config.me_map]
        self.uiMap = ui_maps[self.config.ui_map]

        self.state = {}
        self.raw_control_key_map: dict[str, dict[int, RawControl]] = {}
        for device in config.controls:

            self.state = {
                **self.state,
                **self.create_state(self.config.controls[device])}

            self.raw_control_key_map[device] = self.create_raw_control_key_map(self.config.controls[device])


    @staticmethod
    def check_for_new_connections(config: ControllerConfig) -> bool:
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        connected_controllers = get_controller_manager_state()['controllers']
        connected_ids = [c['id'] for c in connected_controllers]
        for device in devices:
            vendor_match = device.info.vendor == config.vendor
            product_match = device.info.product == config.product
            new_id = device.uniq not in connected_ids
            if (vendor_match and product_match and new_id):
                print("found new Controller Device: " + device.name)
                return True
        return False

    def check_if_still_connected(self) -> bool:
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        connected_ids = [d.uniq for d in devices]
        return self.id in connected_ids

    def open(self, id: str, devices: dict[str, InputDevice], recording: bool = False) -> None:
        self.id = id
        self.devices = devices
        self._recording = recording
        connected_controllers = get_controller_manager_state()['controllers']
        roles = [c['role'] for c in connected_controllers]
        role = 'primary'
        if 'primary' in roles:
            role = 'secondary'

        # Shared event queues: reader threads append, asyncio task consumes
        # Button/pad events are queued individually (order matters)
        # Analog events store only the latest value per code (only latest matters)
        self._discreteEventQueue = collections.deque()  # thread-safe deque
        self._latestAnalogValues = {}  # (device_key, code) -> event
        self._analogLock = threading.Lock()
        self._recordLock = threading.Lock()

        self.data = {
            'id': id,
            'name': self.config.name,
            'role': role,
            'meMap': self.meMap,
            'uiMap': self.uiMap,
            'compatibleMeMaps': self.config.compatible_me_maps
        }
        self.is_connected = True

        for key in devices:
            thread = threading.Thread(
                target=self._device_read_thread,
                args=(key,),
                daemon=True
            )
            thread.start()

        # Single asyncio task processes all queued events
        _task = asyncio.ensure_future(self._process_loop())

        store.dispatch(actions.add(self.data))

    def close(self) -> None:
        self.is_connected = False
        store.dispatch(actions.remove(self.data))
        print(f"Closing connection for {self.config.product}:{self.config.vendor}:{self.id}")

    def _device_read_thread(self, device_key: str) -> None:
        """Dedicated thread: reads evdev as fast as possible, never does processing."""
        button_states = {}
        button_stats = {"presses": 0, "releases": 0, "orphan_releases": 0, "missing_releases": 0}

        # Recording: writes raw events to /tmp/evdev_recording.jsonl
        record_file = None
        record_file_ctx = None
        if self._recording:
            import json
            record_file_ctx = open("/tmp/evdev_recording.jsonl", "a", buffering=1)  # noqa: SIM115
            record_file = record_file_ctx

        try:
            assert self.devices is not None
            print(f"[READER] starting for {device_key}, fd={self.devices[device_key].fd}, is_connected={self.is_connected}, id={self.id}", flush=True)
            device = self.devices[device_key]
            _read_count = 0

            while self.is_connected:
                try:
                    r, _, _ = select.select([device.fd], [], [], 1.0)
                except Exception as e:
                    print(f"[READER] {device_key} select() error: {e}", flush=True)
                    break
                if not r:
                    print(f"[READER] {device_key} select() timeout (no data for 1s)", flush=True)
                    continue

                try:
                    events = list(device.read())
                except BlockingIOError:
                    continue

                if not self.is_connected:
                    continue

                for event in events:
                    if event.type == 0:  # EV_SYN — skip
                        continue

                    # Record raw event
                    if record_file:
                        import json
                        line = json.dumps({
                            "t": event.timestamp(),
                            "device": device_key,
                            "type": event.type,
                            "code": event.code,
                            "value": event.value
                        }) + "\n"
                        with self._recordLock:
                            record_file.write(line)

                    if event.type == 1:  # EV_KEY — button/pad, queue every one
                        # Diagnostics
                        if device_key == "main":
                            code = event.code
                            val = event.value
                            control_name = self.raw_control_key_map[device_key].get(code)
                            control_name = control_name.key if control_name else f"unknown_{code}"
                            if val == 1:
                                if button_states.get(code):
                                    print(f"[BTN_WARN] {control_name} press without prior release!", flush=True)
                                    button_stats["missing_releases"] += 1
                                button_states[code] = True
                                button_stats["presses"] += 1
                            elif val == 0:
                                if not button_states.get(code):
                                    print(f"[BTN_WARN] {control_name} release without prior press!", flush=True)
                                    button_stats["orphan_releases"] += 1
                                button_states[code] = False
                                button_stats["releases"] += 1
                            print(f"[EVDEV] {control_name} val={val} | press={button_stats['presses']} rel={button_stats['releases']} orphan={button_stats['orphan_releases']} miss={button_stats['missing_releases']}", flush=True)

                        self._discreteEventQueue.append((device_key, event))

                    elif event.type == 3:  # EV_ABS — analog, keep only latest per axis
                        with self._analogLock:
                            self._latestAnalogValues[(device_key, event.code)] = event

                _read_count += 1
                if _read_count % 1000 == 0:
                    print(f"[READER] {device_key} alive, {_read_count} reads, queue_size={len(self._latestAnalogValues)}", flush=True)

        except OSError as e:
            self.is_connected = False
            print(f"[READER] device disconnected {device_key}: {e}")
        except Exception:
            self.is_connected = False
            print(f"[READER] error in {device_key}")
            traceback.print_exc()
        finally:
            if record_file_ctx is not None:
                record_file_ctx.close()

    async def _process_loop(self) -> None:
        """Asyncio task: processes queued events on the main thread at a controlled rate."""
        process_interval = 0.005  # 200Hz — fast enough for responsive controls
        _loop_count = 0
        _total_process_time = 0

        while self.is_connected or not self.id:
            await asyncio.sleep(process_interval)

            if not self.is_connected:
                continue

            loop_start = time.monotonic()

            # 1. Process ALL queued discrete events (buttons/pads) — order preserved, none dropped
            discrete_count = 0
            while self._discreteEventQueue:
                device_key, event = self._discreteEventQueue.popleft()
                discrete_count += 1
                try:
                    self.process_event(event, device_key)
                except Exception as e:
                    print(f"error processing discrete event (code={event.code}, value={event.value}): {e}", flush=True)

            # 2. Process latest analog values (one per axis — skips redundant intermediate values)
            with self._analogLock:
                analog_snapshot = dict(self._latestAnalogValues)
                self._latestAnalogValues.clear()

            for (device_key, _), event in analog_snapshot.items():
                try:
                    self.process_event(event, device_key)
                except Exception as e:
                    print(f"error processing analog event (code={event.code}, value={event.value}): {e}", flush=True)

            elapsed = time.monotonic() - loop_start
            _loop_count += 1
            _total_process_time += elapsed
            if _loop_count % 200 == 0:  # print every ~1 second
                avg = (_total_process_time / _loop_count) * 1000
                print(f"[LOOP] avg={avg:.1f}ms  discrete={discrete_count}  analog={len(analog_snapshot)}  elapsed={elapsed*1000:.1f}ms", flush=True)


    def create_state(self, controls: list[RawControl]) -> dict[str, Any]:
        state: dict[str, Any] = {}
        for control in controls:
            if control.type in [RawControlType.BUTTON, RawControlType.PAD]:
                state[control.key] = 0
            elif control.type == RawControlType.ANALOG:
                state[control.key] = {"value_history": [], "threshold_value": 0}
        return state

    def create_raw_control_key_map(self, controls: list[RawControl]) -> dict[int, RawControl]:
        map = {}
        for control in controls:
            map[control.ev_dev_key] = control
        return map

    def get_controls(self) -> dict[str, MappableControl]:
        mappable_controls: dict[str, MappableControl] = {}
        for device in self.config.controls:
            mappable_controls = {
                **mappable_controls,
                **self.create_mappable_controls(self.config.controls[device])}
        return mappable_controls

    def create_mappable_controls(self, controls: list[RawControl]) -> dict[str, MappableControl]:
        assert self.id is not None
        mappable_controls = {}
        for control in controls:
            #BUTTON ON_OFF controls
            if control.type == RawControlType.BUTTON:
                keys = control.get_mappable_control_keys()
                assert keys is not None
                key = keys[0]
                mappable_controls[key] = MappableControl(
                    label=control.label,
                    key=key,
                    raw_control_key=control.key,
                    controller_id=self.id,
                    type=MappableControlType.ON_OFF,
                )
            elif control.type in [RawControlType.PAD, RawControlType.ANALOG]:
                assert control.config is not None
                #ANALOG and PAD ON_OFF controls
                if control.config.expose_on_off_events:
                    for event in [RawControlEvent.DOWN, RawControlEvent.UP, RawControlEvent.LEFT, RawControlEvent.RIGHT]:
                        assert control.config.polar_event_map is not None
                        if (event in control.config.polar_event_map.values()):
                            keys = control.get_mappable_control_keys(MappableControlType.ON_OFF, event)
                            assert keys is not None
                            key = keys[0]
                            mappable_controls[key] = MappableControl(
                                label=control.label + " " + event.name.lower().capitalize(),
                                key=key,
                                raw_control_key=control.key,
                                controller_id=self.id,
                                type=MappableControlType.ON_OFF,
                            )
                #ANALOG and PAD POLAR controls
                if control.config.expose_polar_events:
                    keys = control.get_mappable_control_keys(MappableControlType.POLAR)
                    assert keys is not None
                    key = keys[0]
                    mappable_controls[key] = MappableControl(
                        label=control.label + (" Incremental" if control.type == RawControlType.ANALOG else ""),
                        key=key,
                        raw_control_key=control.key,
                        controller_id=self.id,
                        type=MappableControlType.POLAR,
                    )
            #ANALOG update controls
            if control.type == RawControlType.ANALOG:
                keys = control.get_mappable_control_keys(MappableControlType.ANALOG)
                assert keys is not None
                key = keys[0]
                mappable_controls[key] = MappableControl(
                    label=control.label,
                    key=key,
                    raw_control_key=control.key,
                    controller_id=self.id,
                    type=MappableControlType.ANALOG,
                )
        return mappable_controls


    def process_event(self, event: InputEvent, device: str) -> None:
        if event.code in self.raw_control_key_map[device]:
            control = self.raw_control_key_map[device][event.code]
            if control.type == RawControlType.BUTTON:
                self.process_button_event(event, control)
            elif control.type == RawControlType.PAD:
                self.process_pad_event(event, control)
            elif control.type == RawControlType.ANALOG:
                control_state = self.state[control.key]
                self.process_analog_event(event, control, control_state)

    def process_pad_event(self, event: InputEvent, control: RawControl) -> None:
        assert control.config is not None
        assert control.config.polar_event_map is not None
        if event.value not in control.config.polar_event_map:
            return
        raw_event = control.config.polar_event_map[event.value]

        if control.config.expose_on_off_events:
            self.__send_events(control, raw_event, MappableControlType.ON_OFF)

        if control.config.expose_polar_events:
            self.__send_events(control, raw_event, MappableControlType.POLAR)

    def process_button_event(self, event: InputEvent, control: RawControl) -> None:
        if event.value == 2:  # evdev repeat event — ignore, not a real press/release
            print(f"[BTN_REPEAT] {control.key} (ignored)", flush=True)
            return
        raw_event = RawControlEvent.ON if event.value == 1 else RawControlEvent.OFF
        print(f"[BTN] {control.key} -> {raw_event.name}", flush=True)
        self.__send_events(control, raw_event, MappableControlType.ON_OFF)
        self.state[control.key] = event.value

    def process_analog_event(self, event: InputEvent, control: RawControl, control_state: dict[str, Any]) -> None:
        assert control.config is not None
        assert control.config.top_value is not None
        assert control.config.bottom_value is not None
        assert control.config.average_count is not None
        top = control.config.top_value
        bottom = control.config.bottom_value

        ignore_value = False
        if (control.config.ignore_values is not None
                and event.value in control.config.ignore_values):
            ignore_value = True

        #ensure that value is not erroneously big or small
        if abs(event.value) > 1.25 * max(top, bottom):
            ignore_value = True

        if not ignore_value:

            # update value history
            value_history = control_state["value_history"]
            value_history.append(event.value)
            if (len(value_history) > control.config.average_count):
                value_history.pop(0)

            # get the average of the past raw values (prevents fluttering)
            sum = 0
            for val in value_history:
                sum += val
            average_value = sum / len(value_history)

            #normalize value to between -0.999 and 0.999
            slope = 2.0 / (top - bottom)
            intercept = 1 - (slope * top)
            normalized_value =  (slope * average_value) + intercept
            normalized_value = max(min(normalized_value, 0.999), -0.999)

            self.__send_events(control, RawControlEvent.UPDATE, MappableControlType.ANALOG, normalized_value)

            self.process_threshold(normalized_value, control, control_state)

    def process_threshold(self, normalized_value: float, control: RawControl, control_state: dict[str, Any]) -> None:
        assert control.config is not None
        if control.config.centered_threshold is not None:

            threshold_value = 0
            if control.config.threshold is not None:
                threshold = -1 + (control.config.threshold * 2)
                if normalized_value > threshold:
                    threshold_value = 1
            else:
                if normalized_value > control.config.centered_threshold:
                    threshold_value = 1
                elif normalized_value < -1 * control.config.centered_threshold:
                    threshold_value = -1

            threshold_value_changed = threshold_value != control_state["threshold_value"]

            # update threshold state
            control_state["threshold_value"] = threshold_value

            if threshold_value_changed:

                assert control.config.polar_event_map is not None
                raw_event = control.config.polar_event_map[threshold_value]

                if control.config.expose_on_off_events:
                    self.__send_events(control, raw_event, MappableControlType.ON_OFF)

                if control.config.expose_polar_events:
                    self.__send_events(control, raw_event, MappableControlType.POLAR)

    def __send_events(
        self,
        control: RawControl,
        raw_event: RawControlEvent,
        mappable_control_type: MappableControlType,
        value: float | None = None):

        assert self.id is not None
        mappable_event = control.get_mappable_control_event(mappable_control_type, raw_event)
        keys = control.get_mappable_control_keys(mappable_control_type, raw_event)
        if keys is None or mappable_event is None:
            return

        for key in keys:
            self.send_event(ControlEvent(
                control_key=key,
                event=mappable_event,
                controller_id=self.id,
                value=value
            ))
