from enum import Enum

from pyrsistent import thaw

from controllerCoupler.controlMaps.defaultControlMap import defaultControlMap
from controllerCoupler.models.controlMap import ControlMap
from controllerManager.models.controlEvent import ControlEvent
from controllerManager.models.mappableControl import MappableControl
from controllerManager.models.mappableControlEvent import MappableControlEvent
from eventTrace import trace
from models.appParameter import AppParameter, AppParameterType
from models.command import Command
from models.commandType import CommandType
from redux import store
from redux import utils as reduxUtils
from redux.actions import controllerCoupler as actions


class ChordEngineControlMode(Enum):
    INTERNAL = 'internal'
    EXTERNAL = 'external'

class ControllerCoupler:

    parameters: dict[str, AppParameter]
    controls: dict[str, dict[str, MappableControl]]
    map: ControlMap
    chordEngineControlMode: ChordEngineControlMode

    connectedControllerId: str

    def __init__(self):
        self.map = defaultControlMap
        self.parameters = {}
        self.controls = {}
        self.chordEngineControlMode = ChordEngineControlMode.INTERNAL
        store.dispatch(actions.updateControlMap(self.map))

        store.subscribe(self.handleStoreUpdate)

    def eventHandler(self, event: ControlEvent):
        trace("COUPLER_IN", f"key={event.controlKey} event={event.event.name if event.event else None}")
        if event.controlKey in self.map.map:
            parameterKeys = self.map.map[event.controlKey]
            for parameterKey in parameterKeys:
                if parameterKey in self.parameters:
                    parameter = self.parameters[parameterKey]
                    if self.__useParameter(parameter):
                        command = self.__mapControlEventToParameterEvent(event.event, parameter)
                        if command in parameter.commandMappings:
                            trace("COUPLER_EXEC", f"param={parameterKey} cmd={command.name}")
                            if event.event == MappableControlEvent.UPDATE:
                                parameter.commandMappings[command](event.value)
                            else:
                                parameter.commandMappings[command]()
                        else:
                            trace("COUPLER_DROP", f"param={parameterKey} cmd={command} not in commandMappings")
                    else:
                        trace("COUPLER_DROP", f"param={parameterKey} filtered by chordEngineMode={self.chordEngineControlMode.value}")
                else:
                    trace("COUPLER_DROP", f"paramKey={parameterKey} not in parameters")
        else:
            trace("COUPLER_DROP", f"key={event.controlKey} not in control map")

    def handleStoreUpdate(self):
        state = store.get_state()['controllerCoupler']
        if len(state['appParameters']) != len(self.parameters):
            self.parameters = state['appParameters']
            newParams = self.processNewParameters(state['appParameters'])
            if len(newParams) > 0:
                reduxUtils.addAppParameters(newParams)
            print(f"updating parameters. count: {len(self.parameters)}")
        if len(state['controls'].keys()) != len(self.controls.keys()):
            print("updating controls")
            self.controls = state['controls']

        meState = thaw(store.get_state()['musicEngine'])
        if (meState['chordEngineControl'] != self.chordEngineControlMode.value):
            if (meState['chordEngineControl'] == ChordEngineControlMode.INTERNAL.value):
                self.chordEngineControlMode = ChordEngineControlMode.INTERNAL
            else:
                self.chordEngineControlMode = ChordEngineControlMode.EXTERNAL

    def processNewParameters(self, parameters: dict[str, AppParameter]):

        parameterstoAdd = []

        for key, parameter in parameters.items():

            for incrementalCommand in [Command.INCREMENT, Command.DECREMENT]:

                sign = "+" if incrementalCommand == Command.INCREMENT else "-"
                newKey = f"INCREMENT_{key}" if incrementalCommand == Command.INCREMENT else f"DECREMENT_{key}"
                labelPrefix = "Increment" if incrementalCommand == Command.INCREMENT else "Decrement"

                keyNotInExistingParameters = newKey not in self.parameters
                keyNotInNewParameters = newKey not in parameters

                if incrementalCommand in parameter.commandMappings and keyNotInExistingParameters and keyNotInNewParameters:

                    parameterstoAdd.append(
                        AppParameter(
                            validCommandTypes=[CommandType.ON_OFF],
                            commandMappings={Command.ON: parameter.commandMappings[incrementalCommand]},
                            key=newKey,
                            label=f"{labelPrefix} {parameter.label}",
                            labelAbreviation=f"{sign}{parameter.labelAbreviation}",
                            remappable=False
                    ))

        return parameterstoAdd

    def __useParameter(self, parameter: AppParameter):
        internalMode = self.chordEngineControlMode == ChordEngineControlMode.INTERNAL
        if parameter.type == AppParameterType.INTERNAL_CHORD_ENGINE and not internalMode:
            return False
        return not (parameter.type == AppParameterType.EXTERNAL_CHORD_ENGINE and internalMode)

    def __mapControlEventToParameterEvent(
            self,
            mappableControlEvent: MappableControlEvent,
            parameter: AppParameter
            ) -> Command:

        if (mappableControlEvent == MappableControlEvent.ON):
            if CommandType.TOGGLE in parameter.validCommandTypes:
                return Command.TOGGLE
            if CommandType.ON_OFF in parameter.validCommandTypes:
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
        return None
