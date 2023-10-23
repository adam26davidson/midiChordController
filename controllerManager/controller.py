from abc import ABC, abstractmethod, abstractproperty
import asyncio
import traceback
from typing import List, Dict
from controllerManager.models.controlEvent import ControlEvent

from controllerManager.models.mappableControlEvent import MappableControlEvent
from controllerManager.models.polarOrientation import PolarOrientation
from .models.mappableControl import MappableControl
from .models.mappableControlType import MappableControlType
from .models.rawControl import RawControl
from .models.controllerConfig import ControllerConfig
from .models.rawControlType import RawControlType
from .models.rawControlEvent import RawControlEvent
from .maps import meMaps, uiMaps
from redux import store
from redux.actions import controllerManager as actions
import evdev

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
        self.rawControlKeyMap: Dict[str, Dict[int, RawControl]] = {}
        for device in config.controls.keys():

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

    def open(self, id, devices):
        self.id = id
        self.devices = devices
        connectedControllers = store.get_state()['controllerManager']['controllers']
        roles = [c['role'] for c in connectedControllers]
        role = 'primary'
        if 'primary' in roles: role = 'secondary'
        for key in devices.keys():
            asyncio.ensure_future(self.deviceReadLoop(key))
        self.data = {
            'id': id,
            'name': self.config.name,
            'role': role,
            'meMap': self.meMap,
            'uiMap': self.uiMap,
            'compatibleMeMaps': self.config.compatibleMeMaps
        }
        self.isConnected = True
        store.dispatch(actions.add(self.data))

    def close(self):
        self.isConnected = False
        store.dispatch(actions.remove(self.data))
        print(f"Closing connection for {self.config.product}:{self.config.vendor}:{self.id}")

    async def deviceReadLoop(self, deviceKey):
        try:
            print(f"attempting to enter event loop fors {deviceKey}")
            eventReadLoopGenerator = self.devices[deviceKey].async_read_loop()
            async for event in eventReadLoopGenerator:
                if self.isConnected:
                    self.processEvent(event, deviceKey)
        except Exception as e:
            self.isConnected = False
            print("cannot read event from async_read_loop")
            traceback.print_exc()
            print(e)
            

    def createState(self, controls: List[RawControl]):
        state = {}
        for control in controls:
            if control.type in [RawControlType.BUTTON, RawControlType.PAD]:
                state[control.key] = 0
            elif control.type == RawControlType.ANALOG:
                state[control.key] = {"valueHistory": [], "thresholdValue": 0}
        return state
  
    def createRawControlKeyMap(self, controls: List[RawControl]) -> Dict[int, RawControl]:
        map = {}
        for control in controls:
            map[control.evDevKey] = control
        return map
    
    def getControls(self) -> Dict[str, MappableControl]:
        mappableControls: Dict[str, MappableControl] = {}
        for device in self.config.controls.keys():
            mappableControls = {
                **mappableControls, 
                **self.createMappableControls(self.config.controls[device])}
        return mappableControls
  
    def createMappableControls(self, controls: List[RawControl]) -> Dict[str, MappableControl]:
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
        if event.code in self.rawControlKeyMap[device].keys():
            control = self.rawControlKeyMap[device][event.code]
            if control.type == RawControlType.BUTTON:
                self.processButtonEvent(event, control)
            elif control.type == RawControlType.PAD:
                self.processPadEvent(event, control)
            elif control.type == RawControlType.ANALOG:
                controlState = self.state[control.key]
                self.processAnalogEvent(event, control, controlState)

    def processPadEvent(self, event, control: RawControl):

        rawEvent = control.config.polarEventMap[event.value]

        if control.config.exposeOnOffEvents:
            self.__sendEvents(control, rawEvent, MappableControlType.ON_OFF)

        if control.config.exposePolarEvents:
            self.__sendEvents(control, rawEvent, MappableControlType.POLAR)

    def processButtonEvent(self, event, control: RawControl):
        rawEvent = RawControlEvent.ON if event.value == 1 else RawControlEvent.OFF
        self.__sendEvents(control, rawEvent, MappableControlType.ON_OFF)
        self.state[control.key] = event.value

    def processAnalogEvent(self, event, control: RawControl, controlState):
        top = control.config.topValue; bottom = control.config.bottomValue

        ignoreValue = False
        if control.config.ignoreValues != None:
            if event.value in control.config.ignoreValues:
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
        if control.config.centeredThreshold != None:

            thresholdValue = 0    
            if control.config.threshold != None:
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
        value: float = None):

        mappableEvent = control.getMappableControlEvent(mappableControlType, rawEvent)
        print(f"sendEvents for {control.label}: {mappableEvent}")
        keys = control.getMappableControlKeys(mappableControlType, rawEvent)

        for key in keys:

            self.sendEvent(ControlEvent(
                controlKey=key,
                event=mappableEvent,
                controllerId=self.id,
                value=value
            ))