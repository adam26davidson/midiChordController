from enum import Enum

from pyrsistent import thaw

from controllerCoupler.controlMaps.defaultControlMap import default_control_map
from controllerCoupler.models.controlMap import ControlMap
from controllerManager.models.controlEvent import ControlEvent
from controllerManager.models.mappableControl import MappableControl
from controllerManager.models.mappableControlEvent import MappableControlEvent
from eventTrace import trace
from models.appParameter import AppParameter, AppParameterType
from models.command import Command
from models.commandType import CommandType
from redux import store
from redux import utils as redux_utils
from redux.actions import controllerCoupler as actions


class ChordEngineControlMode(Enum):
    INTERNAL = 'internal'
    EXTERNAL = 'external'

class ControllerCoupler:

    parameters: dict[str, AppParameter]
    controls: dict[str, dict[str, MappableControl]]
    map: ControlMap
    chord_engine_control_mode: ChordEngineControlMode

    connected_controller_id: str

    def __init__(self):
        self.map = default_control_map
        self.parameters = {}
        self.controls = {}
        self.chord_engine_control_mode = ChordEngineControlMode.INTERNAL
        store.dispatch(actions.update_control_map(self.map))

        store.subscribe(self.handle_store_update)

    def event_handler(self, event: ControlEvent):
        trace("COUPLER_IN", f"key={event.control_key} event={event.event.name if event.event else None}")
        if event.control_key in self.map.map:
            parameter_keys = self.map.map[event.control_key]
            for parameter_key in parameter_keys:
                if parameter_key in self.parameters:
                    parameter = self.parameters[parameter_key]
                    if self.__use_parameter(parameter):
                        command = self.__map_control_event_to_parameter_event(event.event, parameter)
                        if command in parameter.command_mappings:
                            trace("COUPLER_EXEC", f"param={parameter_key} cmd={command.name}")
                            if event.event == MappableControlEvent.UPDATE:
                                parameter.command_mappings[command](event.value)
                            else:
                                parameter.command_mappings[command]()
                        else:
                            trace("COUPLER_DROP", f"param={parameter_key} cmd={command} not in command_mappings")
                    else:
                        trace("COUPLER_DROP", f"param={parameter_key} filtered by chordEngineMode={self.chord_engine_control_mode.value}")
                else:
                    trace("COUPLER_DROP", f"paramKey={parameter_key} not in parameters")
        else:
            trace("COUPLER_DROP", f"key={event.control_key} not in control map")

    def handle_store_update(self):
        state = store.get_state()['controllerCoupler']
        if len(state['appParameters']) != len(self.parameters):
            self.parameters = state['appParameters']
            new_params = self.process_new_parameters(state['appParameters'])
            if len(new_params) > 0:
                redux_utils.add_app_parameters(new_params)
            print(f"updating parameters. count: {len(self.parameters)}")
        if len(state['controls'].keys()) != len(self.controls.keys()):
            print("updating controls")
            self.controls = state['controls']

        me_state = thaw(store.get_state()['musicEngine'])
        if (me_state['chordEngineControl'] != self.chord_engine_control_mode.value):
            if (me_state['chordEngineControl'] == ChordEngineControlMode.INTERNAL.value):
                self.chord_engine_control_mode = ChordEngineControlMode.INTERNAL
            else:
                self.chord_engine_control_mode = ChordEngineControlMode.EXTERNAL

    def process_new_parameters(self, parameters: dict[str, AppParameter]):

        parameters_to_add = []

        for key, parameter in parameters.items():

            for incremental_command in [Command.INCREMENT, Command.DECREMENT]:

                sign = "+" if incremental_command == Command.INCREMENT else "-"
                new_key = f"INCREMENT_{key}" if incremental_command == Command.INCREMENT else f"DECREMENT_{key}"
                label_prefix = "Increment" if incremental_command == Command.INCREMENT else "Decrement"

                key_not_in_existing_parameters = new_key not in self.parameters
                key_not_in_new_parameters = new_key not in parameters

                if incremental_command in parameter.command_mappings and key_not_in_existing_parameters and key_not_in_new_parameters:

                    parameters_to_add.append(
                        AppParameter(
                            valid_command_types=[CommandType.ON_OFF],
                            command_mappings={Command.ON: parameter.command_mappings[incremental_command]},
                            key=new_key,
                            label=f"{label_prefix} {parameter.label}",
                            label_abreviation=f"{sign}{parameter.label_abreviation}",
                            remappable=False
                    ))

        return parameters_to_add

    def __use_parameter(self, parameter: AppParameter):
        internal_mode = self.chord_engine_control_mode == ChordEngineControlMode.INTERNAL
        if parameter.type == AppParameterType.INTERNAL_CHORD_ENGINE and not internal_mode:
            return False
        return not (parameter.type == AppParameterType.EXTERNAL_CHORD_ENGINE and internal_mode)

    def __map_control_event_to_parameter_event(
            self,
            mappable_control_event: MappableControlEvent,
            parameter: AppParameter
            ) -> Command:

        if (mappable_control_event == MappableControlEvent.ON):
            if CommandType.TOGGLE in parameter.valid_command_types:
                return Command.TOGGLE
            if CommandType.ON_OFF in parameter.valid_command_types:
                return Command.ON
        elif (mappable_control_event == MappableControlEvent.OFF):
            return Command.OFF
        elif (mappable_control_event == MappableControlEvent.POSITIVE):
            return Command.INCREMENT
        elif (mappable_control_event == MappableControlEvent.NEGATIVE):
            return Command.DECREMENT
        elif (mappable_control_event == MappableControlEvent.UPDATE):
            return Command.UPDATE
        else:
            return None
        return None
