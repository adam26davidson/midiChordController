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

    def __init__(self):
        self.map = defaultControlMap
        self.parameters = {}
        self.controls = {}
        store.dispatch(actions.updateControlMap(self.map))

        store.subscribe(self.handleStoreUpdate)

    def eventHandler(self, event: ControlEvent):
        if event.controlKey in self.map.map.keys():
            parameterKeys = self.map.map[event.controlKey]
            for parameterKey in parameterKeys:
                if parameterKey in self.parameters.keys():
                    parameter = self.parameters[parameterKey]
                    command = self.__mapControlEventToParameterEvent(event.event, parameter)
                    if command in parameter.commandMappings.keys():
                        if event.event == MappableControlEvent.UPDATE:
                            parameter.commandMappings[command](event.value)
                        else:
                            parameter.commandMappings[command]()

    def handleStoreUpdate(self):
        state = store.get_state()['controllerCoupler']
        if len(state['appParameters']) != len(self.parameters):
            self.parameters = self.processNewParameters(state['appParameters'])
            print(f"updating parameters. count: {len(self.parameters)}")
        if len(state['controls'].keys()) != len(self.controls.keys()):
            print("updating controls")
            self.controls = state['controls']

    def processNewParameters(self, parameters: Dict[str, AppParameter]):

        newParameters = {parameter.key: parameter for parameter in parameters.values()}

        for key, parameter in parameters.items():

            for incrementalCommand in [Command.INCREMENT, Command.DECREMENT]:

                sign = "+" if incrementalCommand == Command.INCREMENT else "-"
                newKey = f"INCREMENT_{key}" if incrementalCommand == Command.INCREMENT else f"DECREMENT_{key}"
                labelPrefix = "Increment" if incrementalCommand == Command.INCREMENT else "Decrement"

                if incrementalCommand in parameter.commandMappings.keys() and newKey not in parameters.keys():
                    
                    newParameters[newKey] = AppParameter(
                        validCommandTypes=[CommandType.ON_OFF],
                        commandMappings={Command.ON: parameter.commandMappings[incrementalCommand]},
                        key=newKey,
                        label=f"{labelPrefix} {parameter.label}",
                        labelAbreviation=f"{parameter.labelAbreviation}{sign}",
                        remappable=False
                    )

        return newParameters

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
        