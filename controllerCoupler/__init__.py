from controllerCoupler.models.controlMap import ControlMap
from controllerManager.models.controlEvent import ControlEvent
from controllerManager.models.mappableControl import MappableControl
from controllerCoupler.controlMaps.defaultControlMap import defaultControlMap
from controllerManager.models.mappableControlEvent import MappableControlEvent
from models.appParameter import AppParameter
from models.command import Command
from models.commandType import CommandType
from redux import store
from redux.actions import controllerCoupler as actions
from pyrsistent import thaw
from typing import Callable, Dict, List


class ControllerCoupler():

    parameters: Dict[str, AppParameter]
    controls: Dict[str, Dict[str, MappableControl]]
    map: ControlMap

    connectedControllerId: str
    getControls: Callable[[], Dict[str, Dict[str, MappableControl]]]

    def __init__(self):
        self.map = defaultControlMap
        actions.updateControlMap(self.map)

    def eventHandler(self, event: ControlEvent):
        if event.controlKey in self.map.map.keys():
            parameters: List[AppParameter] = self.parameters[self.map.map[event.controlKey]]
            for parameter in parameters:
                command = self.__mapControlEventToParameterEvent(event.event, parameter)
                if command in parameter.commandMappings.keys():
                    if event.event == MappableControlEvent.UPDATE:
                        parameter.commandMappings[command](event.value)
                    else:
                        parameter.commandMappings[command]()

    def handleStoreUpdate(self):
        cCouplerState = thaw(store.get_state()['controllerCoupler'])
        if len(cCouplerState['appParameters'].keys()) != len(self.parameters.keys()):
            self.parameters = cCouplerState['appParameters']
        if len(cCouplerState['controls'].keys()) != len(self.controls.keys()):
            print("updating controls")
            self.controls = cCouplerState['controls']

    def __mapControlEventToParameterEvent(
            self,
            mappableControlEvent: MappableControlEvent, 
            parameter: AppParameter
            ) -> Command:
        
        if (mappableControlEvent == MappableControlEvent.ON):
            if (parameter.validCommandTypes.count(CommandType.TOGGLE)):
                return Command.TOGGLE
            elif (parameter.validCommandTypes.count(CommandType.ON_OFF)):
                return Command.ON
        elif (mappableControlEvent == MappableControlEvent.OFF):
            return Command.OFF
        elif (mappableControlEvent == MappableControlEvent.POSITIVE):
            return Command.INCREMENT
        elif (mappableControlEvent == MappableControlEvent.NEGATIVE):
            return Command.DECREMENT
        elif (mappableControlEvent == MappableControlEvent.UPDATE):
            return Command.UPDATE
        else:
            return None
        