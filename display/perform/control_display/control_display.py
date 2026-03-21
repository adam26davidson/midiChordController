from __future__ import annotations

import tkinter as tk
from typing import TYPE_CHECKING

from pyrsistent import thaw

from models.app_parameter import AppParameter, AppParameterType

if TYPE_CHECKING:
    from controller_coupler.models.control_map import ControlMap
from models.command import Command
from models.command_type import CommandType
from redux import store
from redux import utils as redux_utils

from .bumper_button import BumperButton
from .circular_button import CircularButton
from .dpad_button import DPadButton
from .joy_stick_button import JoyStickButton
from .options_button import OptionsButton
from .touch_pad_button import TouchPadButton
from .trigger_button import TriggerButton


class ControlDisplay(tk.Canvas):

    width = 340
    margin = 5
    width_units = 15
    height_units = 14

    parameters: list[AppParameter]

    def __init__(self, master=None):
        self.unit_size = (self.width - (2 * self.margin)) / self.width_units
        self.height = (self.unit_size * self.height_units) + (2 * self.margin)
        super().__init__(master, width=self.width, height=(self.width / self.width_units) * self.height_units,
                         highlightthickness=0, relief="flat", bg="#000000")

        self.parent = master
        self.parameters = []
        self.app_parameter_length = 0
        self.buttons_created = False
        self.chord_engine_control_mode = 'internal'

        self.pack(side="top", anchor="nw", padx=(0, 0), pady=(0, 0))

        self._dirty = False
        store.subscribe(self.__handle_store_update)

    def __handle_store_update(self):
        self._dirty = True

    def check_state(self):
        if not self._dirty:
            return
        self._dirty = False

        me_state = thaw(store.get_state()['musicEngine'])
        if (me_state['chordEngineControl'] != self.chord_engine_control_mode):
            self.chord_engine_control_mode = me_state['chordEngineControl']
            if self.buttons_created:
                state = store.get_state()['controllerCoupler']
                params = state['appParameters']
                control_map: ControlMap = state['activeControlMap']
                if control_map is not None:
                    self.__update_button_params(params, control_map.map)

        state = store.get_state()['controllerCoupler']
        params = state['appParameters']
        control_map: ControlMap = state['activeControlMap']
        music_engine_parameters_loaded = state['musicEngineAppParametersLoaded']
        if control_map is not None and music_engine_parameters_loaded and len(params) != self.app_parameter_length:
            if (not self.buttons_created):
                self.app_parameter_length = len(params)
                self.__create_buttons(params, control_map.map)
                self.buttons_created = True
                redux_utils.add_app_parameters(self.parameters)
            else:
                self.app_parameter_length = len(params)
                self.__update_button_params(params, control_map.map)

    def __create_buttons(self, params, map):

        def get_param(key):
            return self.get_first_me_parameter(params, map, key)

        self.create_main_buttons(get_param)
        self.create_start_button(map, params)
        self.create_dpad_buttons(get_param)
        self.create_options_buttons(get_param)
        self.create_joy_sticks(get_param)
        self.create_bumper_buttons(get_param)
        self.create_trigger_buttons(get_param)
        self.create_touch_pad_button(get_param)

    def __update_button_params(self, params, map):

        def get_param(key):
            return self.get_first_me_parameter(params, map, key)

        self.southButton.set_param(get_param("SOUTH_BUTTON"))
        self.eastButton.set_param(get_param("EAST_BUTTON"))
        self.northButton.set_param(get_param("NORTH_BUTTON"))
        self.westButton.set_param(get_param("WEST_BUTTON"))


        self.startButton.set_param(self.get_start_button_param(map, params))

        left_param, right_param, up_param, down_param, x_type, y_type = self.get_dpad_params(get_param)

        self.dpadDownButton.set_param(down_param, y_type)
        self.dpadUpButton.set_param(up_param, y_type)
        self.dpadLeftButton.set_param(left_param, x_type)
        self.dpadRightButton.set_param(right_param, x_type)

        self.leftOptionButton.set_param(get_param("LEFT_OPTION"))
        self.rightOptionButton.set_param(get_param("RIGHT_OPTION"))

        self.leftTriggerButton.set_param(get_param("LEFT_TRIGGER"))
        self.rightTriggerButton.set_param(get_param("RIGHT_TRIGGER"))

        self.leftBumperButton.set_param(get_param("LEFT_BUMPER"))
        self.rightBumperButton.set_param(get_param("RIGHT_BUMPER"))

        self.touch_pad_button.set_x_param(get_param("TOUCHPAD_X"))
        self.touch_pad_button.set_y_param(get_param("TOUCHPAD_Y"))

        left_x_params, left_x_type = self.get_joystick_axis_params("LEFT_STICK", "X", get_param)
        left_y_params, left_y_type = self.get_joystick_axis_params("LEFT_STICK", "Y", get_param)
        right_x_params, right_x_type = self.get_joystick_axis_params("RIGHT_STICK", "X", get_param)
        right_y_params, right_y_type = self.get_joystick_axis_params("RIGHT_STICK", "Y", get_param)

        self.leftStick.set_x_params(left_x_params, left_x_type)
        self.leftStick.set_y_params(left_y_params, left_y_type)
        self.rightStick.set_x_params(right_x_params, right_x_type)
        self.rightStick.set_y_params(right_y_params, right_y_type)


    def units_to_coord(self, units):
        return self.margin + (units * self.unit_size)

    def create_main_buttons(self, get_param):
        c_x = 12
        c_y = 7.75
        u_to_c = self.units_to_coord
        self.southButton = CircularButton(self, get_param("SOUTH_BUTTON"), u_to_c(c_x), u_to_c(c_y + 2), self.unit_size)
        self.eastButton = CircularButton(self, get_param("EAST_BUTTON"), u_to_c(c_x + 2), u_to_c(c_y), self.unit_size)
        self.northButton = CircularButton(self, get_param("NORTH_BUTTON"), u_to_c(c_x), u_to_c(c_y - 2), self.unit_size)
        self.westButton = CircularButton(self, get_param("WEST_BUTTON"), u_to_c(c_x - 2), u_to_c(c_y), self.unit_size)
        self.parameters.extend([
            AppParameter(
                valid_command_types=[CommandType.ON_OFF],
                command_mappings={Command.ON: self.southButton.on, Command.OFF: self.southButton.off},
                key="UI_SOUTH_BUTTON",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                valid_command_types=[CommandType.ON_OFF],
                command_mappings={Command.ON: self.eastButton.on, Command.OFF: self.eastButton.off},
                key="UI_EAST_BUTTON",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                valid_command_types=[CommandType.ON_OFF],
                command_mappings={Command.ON: self.northButton.on, Command.OFF: self.northButton.off},
                key="UI_NORTH_BUTTON",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                valid_command_types=[CommandType.ON_OFF],
                command_mappings={Command.ON: self.westButton.on, Command.OFF: self.westButton.off},
                key="UI_WEST_BUTTON",
                remappable=False,
                type=AppParameterType.UI
            )
        ])

    def create_trigger_buttons(self, get_param):
        self.leftTriggerButton = TriggerButton(self, get_param("LEFT_TRIGGER"), 2.5, 0.8)
        self.rightTriggerButton = TriggerButton(self, get_param("RIGHT_TRIGGER"), 12.5, 0.8)
        self.parameters.extend([
            AppParameter(
                valid_command_types=[CommandType.ON_OFF],
                command_mappings={Command.ON: self.leftTriggerButton.on, Command.OFF: self.leftTriggerButton.off},
                key="UI_LEFT_TRIGGER",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                valid_command_types=[CommandType.ON_OFF],
                command_mappings={Command.ON: self.rightTriggerButton.on, Command.OFF: self.rightTriggerButton.off},
                key="UI_RIGHT_TRIGGER",
                remappable=False,
                type=AppParameterType.UI
            )
        ])

    def create_bumper_buttons(self, get_param):
        self.leftBumperButton = BumperButton(self, get_param("LEFT_BUMPER"), 2.5, 3.25)
        self.rightBumperButton = BumperButton(self, get_param("RIGHT_BUMPER"), 12.5, 3.25)
        self.parameters.extend([
            AppParameter(
                valid_command_types=[CommandType.ON_OFF],
                command_mappings={Command.ON: self.leftBumperButton.on, Command.OFF: self.leftBumperButton.off},
                key="UI_LEFT_BUMPER",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                valid_command_types=[CommandType.ON_OFF],
                command_mappings={Command.ON: self.rightBumperButton.on, Command.OFF: self.rightBumperButton.off},
                key="UI_RIGHT_BUMPER",
                label="UI Right Bumper",
                label_abreviation=None,
                remappable=False,
                type=AppParameterType.UI
            )
        ])

    def create_touch_pad_button(self, get_param):

        self.touch_pad_button = TouchPadButton(self, get_param("TOUCHPAD_X"), get_param("TOUCHPAD_Y"), 7.5, 1.5)
        self.parameters.extend([
            AppParameter(
                valid_command_types=[CommandType.ANALOG],
                command_mappings={Command.UPDATE: self.touch_pad_button.update_x},
                key="UI_TOUCHPAD_X",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                valid_command_types=[CommandType.ANALOG],
                command_mappings={Command.UPDATE: self.touch_pad_button.update_y},
                key="UI_TOUCHPAD_Y",
                remappable=False,
                type=AppParameterType.UI
            )
        ])

    def create_start_button(self, map, params: dict[str, AppParameter]):
        param = self.get_start_button_param(map, params)

        u_to_c = self.units_to_coord

        self.startButton = CircularButton(self, param, u_to_c(7.5), u_to_c(9.5), self.unit_size)
        self.parameters.extend([
            AppParameter(
                valid_command_types=[CommandType.ON_OFF],
                command_mappings={Command.ON: self.startButton.on, Command.OFF: self.startButton.off},
                key="UI_START_BUTTON",
                remappable=False,
                type=AppParameterType.UI
            )
        ])

    def create_dpad_buttons(self, get_param):

        left_param, right_param, up_param, down_param, x_type, y_type = self.get_dpad_params(get_param)

        cx = 3
        cy = 7.75
        self.dpadDownButton = DPadButton(self, down_param, y_type, "DOWN", cx, cy)
        self.dpadUpButton = DPadButton(self, up_param, y_type, "UP", cx, cy)
        self.dpadLeftButton = DPadButton(self, left_param, x_type, "LEFT", cx, cy)
        self.dpadRightButton = DPadButton(self, right_param, x_type, "RIGHT", cx, cy)
        self.parameters.extend([
            AppParameter(
                valid_command_types=[CommandType.ON_OFF],
                command_mappings={Command.ON: self.dpadDownButton.on, Command.OFF: self.dpadDownButton.off},
                key="UI_DPAD_DOWN",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                valid_command_types=[CommandType.ON_OFF],
                command_mappings={Command.ON: self.dpadUpButton.on, Command.OFF: self.dpadUpButton.off},
                key="UI_DPAD_UP",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                valid_command_types=[CommandType.ON_OFF],
                command_mappings={Command.ON: self.dpadLeftButton.on, Command.OFF: self.dpadLeftButton.off},
                key="UI_DPAD_LEFT",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                valid_command_types=[CommandType.ON_OFF],
                command_mappings={Command.ON: self.dpadRightButton.on, Command.OFF: self.dpadRightButton.off},
                key="UI_DPAD_RIGHT",
                remappable=False,
                type=AppParameterType.UI
            )
        ])

    def create_options_buttons(self, get_param):
        self.leftOptionButton = OptionsButton(self, get_param("LEFT_OPTION"), 6, 4.75, self.unit_size)
        self.rightOptionButton = OptionsButton(self, get_param("RIGHT_OPTION"), 9, 4.75, self.unit_size)
        self.parameters.extend([
            AppParameter(
                valid_command_types=[CommandType.ON_OFF],
                command_mappings={Command.ON: self.leftOptionButton.on, Command.OFF: self.leftOptionButton.off},
                key="UI_LEFT_OPTION",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                valid_command_types=[CommandType.ON_OFF],
                command_mappings={Command.ON: self.rightOptionButton.on, Command.OFF: self.rightOptionButton.off},
                key="UI_RIGHT_OPTION",
                remappable=False,
                type=AppParameterType.UI
            )
        ])

    def create_joy_sticks(self, get_param):

        left_x_params, left_x_type = self.get_joystick_axis_params("LEFT_STICK", "X", get_param)
        left_y_params, left_y_type = self.get_joystick_axis_params("LEFT_STICK", "Y", get_param)
        right_x_params, right_x_type = self.get_joystick_axis_params("RIGHT_STICK", "X", get_param)
        right_y_params, right_y_type = self.get_joystick_axis_params("RIGHT_STICK", "Y", get_param)

        self.leftStick = JoyStickButton(
            self,
            left_x_params, left_y_params, left_x_type, left_y_type,
            get_param("LEFT_STICK_BUTTON"),
            5.25, 12, "LEFT")

        self.rightStick = JoyStickButton(
            self,
            right_x_params, right_y_params, right_x_type, right_y_type,
            get_param("RIGHT_STICK_BUTTON"),
            9.75, 12, "RIGHT")
        self.parameters.extend([
            AppParameter(
                valid_command_types=[CommandType.ON_OFF],
                command_mappings={Command.ON: self.leftStick.button_on, Command.OFF: self.leftStick.button_off},
                key="UI_LEFT_STICK_BUTTON",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                valid_command_types=[CommandType.ON_OFF],
                command_mappings={Command.ON: self.leftStick.left_on, Command.OFF: self.leftStick.left_off},
                key="UI_LEFT_STICK_LEFT",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                valid_command_types=[CommandType.ON_OFF],
                command_mappings={Command.ON: self.leftStick.right_on, Command.OFF: self.leftStick.right_off},
                key="UI_LEFT_STICK_RIGHT",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                valid_command_types=[CommandType.ON_OFF],
                command_mappings={Command.ON: self.leftStick.up_on, Command.OFF: self.leftStick.up_off},
                key="UI_LEFT_STICK_UP",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                valid_command_types=[CommandType.ON_OFF],
                command_mappings={Command.ON: self.leftStick.down_on, Command.OFF: self.leftStick.down_off},
                key="UI_LEFT_STICK_DOWN",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                valid_command_types=[CommandType.ANALOG],
                command_mappings={Command.UPDATE: self.leftStick.update_x},
                key="UI_LEFT_STICK_X",
                remappable=False
            ),
            AppParameter(
                valid_command_types=[CommandType.ANALOG],
                command_mappings={Command.UPDATE: self.leftStick.update_y},
                key="UI_LEFT_STICK_Y",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                valid_command_types=[CommandType.ON_OFF],
                command_mappings={Command.ON: self.rightStick.button_on, Command.OFF: self.rightStick.button_off},
                key="UI_RIGHT_STICK_BUTTON",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                valid_command_types=[CommandType.ON_OFF],
                command_mappings={Command.ON: self.rightStick.left_on, Command.OFF: self.rightStick.left_off},
                key="UI_RIGHT_STICK_LEFT",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                valid_command_types=[CommandType.ON_OFF],
                command_mappings={Command.ON: self.rightStick.right_on, Command.OFF: self.rightStick.right_off},
                key="UI_RIGHT_STICK_RIGHT",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                valid_command_types=[CommandType.ON_OFF],
                command_mappings={Command.ON: self.rightStick.up_on, Command.OFF: self.rightStick.up_off},
                key="UI_RIGHT_STICK_UP",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                valid_command_types=[CommandType.ON_OFF],
                command_mappings={Command.ON: self.rightStick.down_on, Command.OFF: self.rightStick.down_off},
                key="UI_RIGHT_STICK_DOWN",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                valid_command_types=[CommandType.ANALOG],
                command_mappings={Command.UPDATE: self.rightStick.update_x},
                key="UI_RIGHT_STICK_X",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                valid_command_types=[CommandType.ANALOG],
                command_mappings={Command.UPDATE: self.rightStick.update_y},
                key="UI_RIGHT_STICK_Y",
                remappable=False,
                type=AppParameterType.UI
            )
        ])

    def get_start_button_param(self, map, params: dict[str, AppParameter]):
        param = None
        if ("START_BUTTON" in map):
            for parameter_key in map["START_BUTTON"]:
                if (parameter_key in params):
                    param =  params[parameter_key]
        return param

    def get_dpad_params(self, get_param):
        x_polar = get_param("DPAD_X")
        y_polar = get_param("DPAD_Y")
        left = get_param("DPAD_X_LEFT")
        right = get_param("DPAD_X_RIGHT")
        up = get_param("DPAD_Y_UP")
        down = get_param("DPAD_Y_DOWN")

        x_type, y_type = None, None
        left_param, right_param, up_param, down_param = None, None, None, None

        if (x_polar):
            x_type = "POLAR"
            left_param = x_polar
            right_param = x_polar
        elif (left and right):
            x_type = "ON_OFF"
            left_param = left
            right_param = right

        if (y_polar):
            y_type = "POLAR"
            up_param = y_polar
            down_param = y_polar
        elif (up and down):
            y_type = "ON_OFF"
            up_param = up
            down_param = down

        return left_param, right_param, up_param, down_param, x_type, y_type

    def get_joystick_axis_params(self, prefix: str, axis: str, get_param):
        positive_suffix = "RIGHT" if axis == "X" else "UP"
        negative_suffix = "LEFT" if axis == "X" else "DOWN"

        p_param = get_param(f"{prefix}_{axis}_{positive_suffix}")
        n_param = get_param(f"{prefix}_{axis}_{negative_suffix}")
        polar_param = get_param(f"{prefix}_{axis}_POLAR")
        analog_param = get_param(f"{prefix}_{axis}")

        if analog_param:
            return [analog_param], "ANALOG"
        if polar_param:
            return [polar_param], "POLAR"
        if n_param and p_param:
            return [n_param, p_param], "ON_OFF"
        return [], None

    def get_first_me_parameter(self, params: dict[str, AppParameter], map: dict[str, list[str]], key):
        if (key in map):
            for parameter_key in map[key]:
                if (parameter_key in params and params[parameter_key].type != AppParameterType.UI):
                    parameter_type = params[parameter_key].type
                    if (self.chord_engine_control_mode == 'internal' and parameter_type == AppParameterType.INTERNAL_CHORD_ENGINE) or (self.chord_engine_control_mode == 'external' and parameter_type == AppParameterType.EXTERNAL_CHORD_ENGINE):
                        return params[parameter_key]

        return None
