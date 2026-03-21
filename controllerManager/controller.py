from __future__ import annotations

import asyncio
import collections
import select
import threading
import time
import traceback
from abc import ABC

import evdev

from controllerManager.models.controlEvent import ControlEvent
from redux import store
from redux.actions import controllerManager as actions

from .maps import meMaps, uiMaps
from .models.controllerConfig import ControllerConfig
from .models.mappableControl import MappableControl
from .models.mappableControlType import MappableControlType
from .models.rawControl import RawControl
from .models.rawControlEvent import RawControlEvent
from .models.rawControlType import RawControlType


class Controller(ABC):

    config: ControllerConfig

    def __init__(self, sendEvent, info, config: ControllerConfig):
        self.id = None
        self.data = None
        self.isConnected = False
        self.devices = None
        self.sendEvent = sendEvent
        self.config = config
        self.info = info
        self.meMap = meMaps[self.config.meMap]
        self.uiMap = uiMaps[self.config.uiMap]

        self.state = {}
        self.rawControlKeyMap: dict[str, dict[int, RawControl]] = {}
        for device in config.controls:

            self.state = {
                **self.state,
                **self.createState(self.config.controls[device])}

            self.rawControlKeyMap[device] = self.createRawControlKeyMap(self.config.controls[device])


    @staticmethod
    def checkForNewConnections(config: ControllerConfig):
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        connectedControllers = store.get_state()['controllerManager']['controllers']
        connectedIds = [c['id'] for c in connectedControllers]
        for device in devices:
            vendorMatch = device.info.vendor == config.vendor
            productMatch = device.info.product == config.product
            newId = device.uniq not in connectedIds
            if (vendorMatch and productMatch and newId):
                print("found new Controller Device: " + device.name)
                return True
        return False

    def checkIfStillConnected(self):
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        connectedIds = [d.uniq for d in devices]
        return self.id in connectedIds

    def open(self, id, devices, recording=False):
        self.id = id
        self.devices = devices
        self._recording = recording
        connectedControllers = store.get_state()['controllerManager']['controllers']
        roles = [c['role'] for c in connectedControllers]
        role = 'primary'
        if 'primary' in roles:
            role = 'secondary'

        # Shared event queues: reader threads append, asyncio task consumes
        # Button/pad events are queued individually (order matters)
        # Analog events store only the latest value per code (only latest matters)
        self._discreteEventQueue = collections.deque()  # thread-safe deque
        self._latestAnalogValues = {}  # (deviceKey, code) -> event
        self._analogLock = threading.Lock()
        self._recordLock = threading.Lock()

        self.data = {
            'id': id,
            'name': self.config.name,
            'role': role,
            'meMap': self.meMap,
            'uiMap': self.uiMap,
            'compatibleMeMaps': self.config.compatibleMeMaps
        }
        self.isConnected = True

        for key in devices:
            thread = threading.Thread(
                target=self._deviceReadThread,
                args=(key,),
                daemon=True
            )
            thread.start()

        # Single asyncio task processes all queued events
        _task = asyncio.ensure_future(self._processLoop())

        store.dispatch(actions.add(self.data))

    def close(self):
        self.isConnected = False
        store.dispatch(actions.remove(self.data))
        print(f"Closing connection for {self.config.product}:{self.config.vendor}:{self.id}")

    def _deviceReadThread(self, deviceKey):
        """Dedicated thread: reads evdev as fast as possible, never does processing."""
        buttonStates = {}
        buttonStats = {"presses": 0, "releases": 0, "orphan_releases": 0, "missing_releases": 0}

        # Recording: writes raw events to /tmp/evdev_recording.jsonl
        recordFile = None
        recordFileCtx = None
        if self._recording:
            import json
            recordFileCtx = open("/tmp/evdev_recording.jsonl", "a", buffering=1)  # noqa: SIM115
            recordFile = recordFileCtx

        try:
            print(f"[READER] starting for {deviceKey}, fd={self.devices[deviceKey].fd}, isConnected={self.isConnected}, id={self.id}", flush=True)
            device = self.devices[deviceKey]
            _readCount = 0

            while self.isConnected:
                try:
                    r, _, _ = select.select([device.fd], [], [], 1.0)
                except Exception as e:
                    print(f"[READER] {deviceKey} select() error: {e}", flush=True)
                    break
                if not r:
                    print(f"[READER] {deviceKey} select() timeout (no data for 1s)", flush=True)
                    continue

                try:
                    events = list(device.read())
                except BlockingIOError:
                    continue

                if not self.isConnected:
                    continue

                for event in events:
                    if event.type == 0:  # EV_SYN — skip
                        continue

                    # Record raw event
                    if recordFile:
                        import json
                        line = json.dumps({
                            "t": event.timestamp(),
                            "device": deviceKey,
                            "type": event.type,
                            "code": event.code,
                            "value": event.value
                        }) + "\n"
                        with self._recordLock:
                            recordFile.write(line)

                    if event.type == 1:  # EV_KEY — button/pad, queue every one
                        # Diagnostics
                        if deviceKey == "main":
                            code = event.code
                            val = event.value
                            controlName = self.rawControlKeyMap[deviceKey].get(code)
                            controlName = controlName.key if controlName else f"unknown_{code}"
                            if val == 1:
                                if buttonStates.get(code):
                                    print(f"[BTN_WARN] {controlName} press without prior release!", flush=True)
                                    buttonStats["missing_releases"] += 1
                                buttonStates[code] = True
                                buttonStats["presses"] += 1
                            elif val == 0:
                                if not buttonStates.get(code):
                                    print(f"[BTN_WARN] {controlName} release without prior press!", flush=True)
                                    buttonStats["orphan_releases"] += 1
                                buttonStates[code] = False
                                buttonStats["releases"] += 1
                            print(f"[EVDEV] {controlName} val={val} | press={buttonStats['presses']} rel={buttonStats['releases']} orphan={buttonStats['orphan_releases']} miss={buttonStats['missing_releases']}", flush=True)

                        self._discreteEventQueue.append((deviceKey, event))

                    elif event.type == 3:  # EV_ABS — analog, keep only latest per axis
                        with self._analogLock:
                            self._latestAnalogValues[(deviceKey, event.code)] = event

                _readCount += 1
                if _readCount % 1000 == 0:
                    print(f"[READER] {deviceKey} alive, {_readCount} reads, queue_size={len(self._latestAnalogValues)}", flush=True)

        except OSError as e:
            self.isConnected = False
            print(f"[READER] device disconnected {deviceKey}: {e}")
        except Exception:
            self.isConnected = False
            print(f"[READER] error in {deviceKey}")
            traceback.print_exc()
        finally:
            if recordFileCtx is not None:
                recordFileCtx.close()

    async def _processLoop(self):
        """Asyncio task: processes queued events on the main thread at a controlled rate."""
        PROCESS_INTERVAL = 0.005  # 200Hz — fast enough for responsive controls
        _loopCount = 0
        _totalProcessTime = 0

        while self.isConnected or not self.id:
            await asyncio.sleep(PROCESS_INTERVAL)

            if not self.isConnected:
                continue

            loopStart = time.monotonic()

            # 1. Process ALL queued discrete events (buttons/pads) — order preserved, none dropped
            discreteCount = 0
            while self._discreteEventQueue:
                deviceKey, event = self._discreteEventQueue.popleft()
                discreteCount += 1
                try:
                    self.processEvent(event, deviceKey)
                except Exception as e:
                    print(f"error processing discrete event (code={event.code}, value={event.value}): {e}", flush=True)

            # 2. Process latest analog values (one per axis — skips redundant intermediate values)
            with self._analogLock:
                analogSnapshot = dict(self._latestAnalogValues)
                self._latestAnalogValues.clear()

            for (deviceKey, _), event in analogSnapshot.items():
                try:
                    self.processEvent(event, deviceKey)
                except Exception as e:
                    print(f"error processing analog event (code={event.code}, value={event.value}): {e}", flush=True)

            elapsed = time.monotonic() - loopStart
            _loopCount += 1
            _totalProcessTime += elapsed
            if _loopCount % 200 == 0:  # print every ~1 second
                avg = (_totalProcessTime / _loopCount) * 1000
                print(f"[LOOP] avg={avg:.1f}ms  discrete={discreteCount}  analog={len(analogSnapshot)}  elapsed={elapsed*1000:.1f}ms", flush=True)


    def createState(self, controls: list[RawControl]):
        state = {}
        for control in controls:
            if control.type in [RawControlType.BUTTON, RawControlType.PAD]:
                state[control.key] = 0
            elif control.type == RawControlType.ANALOG:
                state[control.key] = {"valueHistory": [], "thresholdValue": 0}
        return state

    def createRawControlKeyMap(self, controls: list[RawControl]) -> dict[int, RawControl]:
        map = {}
        for control in controls:
            map[control.evDevKey] = control
        return map

    def getControls(self) -> dict[str, MappableControl]:
        mappableControls: dict[str, MappableControl] = {}
        for device in self.config.controls:
            mappableControls = {
                **mappableControls,
                **self.createMappableControls(self.config.controls[device])}
        return mappableControls

    def createMappableControls(self, controls: list[RawControl]) -> dict[str, MappableControl]:
        mappableControls = {}
        for control in controls:
            #BUTTON ON_OFF controls
            if control.type == RawControlType.BUTTON:
                key = control.getMappableControlKeys()[0]
                mappableControls[key] = MappableControl(
                    label=control.label,
                    key=key,
                    rawControlKey=control.key,
                    controllerId=self.id,
                    type=MappableControlType.ON_OFF,
                )
            elif control.type in [RawControlType.PAD, RawControlType.ANALOG]:
                #ANALOG and PAD ON_OFF controls
                if control.config.exposeOnOffEvents:
                    for event in [RawControlEvent.DOWN, RawControlEvent.UP, RawControlEvent.LEFT, RawControlEvent.RIGHT]:
                        if (event in control.config.polarEventMap.values()):
                            key = control.getMappableControlKeys(MappableControlType.ON_OFF, event)[0]
                            mappableControls[key] = MappableControl(
                                label=control.label + " " + event.name.lower().capitalize(),
                                key=key,
                                rawControlKey=control.key,
                                controllerId=self.id,
                                type=MappableControlType.ON_OFF,
                            )
                #ANALOG and PAD POLAR controls
                if control.config.exposePolarEvents:
                    key = control.getMappableControlKeys(MappableControlType.POLAR)[0]
                    mappableControls[key] = MappableControl(
                        label=control.label + (" Incremental" if control.type == RawControlType.ANALOG else ""),
                        key=key,
                        rawControlKey=control.key,
                        controllerId=self.id,
                        type=MappableControlType.POLAR,
                    )
            #ANALOG update controls
            if control.type == RawControlType.ANALOG:
                key = control.getMappableControlKeys(MappableControlType.ANALOG)[0]
                mappableControls[key] = MappableControl(
                    label=control.label,
                    key=key,
                    rawControlKey=control.key,
                    controllerId=self.id,
                    type=MappableControlType.ANALOG,
                )
        return mappableControls


    def processEvent(self, event, device):
        if event.code in self.rawControlKeyMap[device]:
            control = self.rawControlKeyMap[device][event.code]
            if control.type == RawControlType.BUTTON:
                self.processButtonEvent(event, control)
            elif control.type == RawControlType.PAD:
                self.processPadEvent(event, control)
            elif control.type == RawControlType.ANALOG:
                controlState = self.state[control.key]
                self.processAnalogEvent(event, control, controlState)

    def processPadEvent(self, event, control: RawControl):

        if event.value not in control.config.polarEventMap:
            return
        rawEvent = control.config.polarEventMap[event.value]

        if control.config.exposeOnOffEvents:
            self.__sendEvents(control, rawEvent, MappableControlType.ON_OFF)

        if control.config.exposePolarEvents:
            self.__sendEvents(control, rawEvent, MappableControlType.POLAR)

    def processButtonEvent(self, event, control: RawControl):
        if event.value == 2:  # evdev repeat event — ignore, not a real press/release
            print(f"[BTN_REPEAT] {control.key} (ignored)", flush=True)
            return
        rawEvent = RawControlEvent.ON if event.value == 1 else RawControlEvent.OFF
        print(f"[BTN] {control.key} -> {rawEvent.name}", flush=True)
        self.__sendEvents(control, rawEvent, MappableControlType.ON_OFF)
        self.state[control.key] = event.value

    def processAnalogEvent(self, event, control: RawControl, controlState):
        top = control.config.topValue
        bottom = control.config.bottomValue

        ignoreValue = False
        if (control.config.ignoreValues is not None
                and event.value in control.config.ignoreValues):
            ignoreValue = True

        #ensure that value is not erroneously big or small
        if abs(event.value) > 1.25 * max(top, bottom):
            ignoreValue = True

        if not ignoreValue:

            # update value history
            valueHistory = controlState["valueHistory"]
            valueHistory.append(event.value)
            if (len(valueHistory) > control.config.averageCount):
                valueHistory.pop(0)

            # get the average of the past raw values (prevents fluttering)
            sum = 0
            for val in valueHistory:
                sum += val
            averageValue = sum / len(valueHistory)

            #normalize value to between -0.999 and 0.999
            slope = 2.0 / (top - bottom)
            intercept = 1 - (slope * top)
            normalizedValue =  (slope * averageValue) + intercept
            normalizedValue = max(min(normalizedValue, 0.999), -0.999)

            self.__sendEvents(control, RawControlEvent.UPDATE, MappableControlType.ANALOG, normalizedValue)

            self.processThreshold(normalizedValue, control, controlState)

    def processThreshold(self, normalizedValue, control: RawControl, controlState):
        if control.config.centeredThreshold is not None:

            thresholdValue = 0
            if control.config.threshold is not None:
                threshold = -1 + (control.config.threshold * 2)
                if normalizedValue > threshold:
                    thresholdValue = 1
            else:
                if normalizedValue > control.config.centeredThreshold:
                    thresholdValue = 1
                elif normalizedValue < -1 * control.config.centeredThreshold:
                    thresholdValue = -1

            thresholdValueChanged = thresholdValue != controlState["thresholdValue"]

            # update threshold state
            controlState["thresholdValue"] = thresholdValue

            if thresholdValueChanged:

                rawEvent = control.config.polarEventMap[thresholdValue]

                if control.config.exposeOnOffEvents:
                    self.__sendEvents(control, rawEvent, MappableControlType.ON_OFF)

                if control.config.exposePolarEvents:
                    self.__sendEvents(control, rawEvent, MappableControlType.POLAR)

    def __sendEvents(
        self,
        control: RawControl,
        rawEvent: RawControlEvent,
        mappableControlType: MappableControlType,
        value: float | None = None):

        mappableEvent = control.getMappableControlEvent(mappableControlType, rawEvent)
        keys = control.getMappableControlKeys(mappableControlType, rawEvent)

        for key in keys:
            self.sendEvent(ControlEvent(
                controlKey=key,
                event=mappableEvent,
                controllerId=self.id,
                value=value
            ))
