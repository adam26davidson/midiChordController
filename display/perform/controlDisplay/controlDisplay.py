import tkinter as tk
from typing import Dict, List
from controllerCoupler.models.controlMap import ControlMap
from controllerManager.maps.me.controlAbreviations import controlAbreviations as CONTROL_ABREVIATIONS
from models.appParameter import AppParameter, AppParameterType
from models.command import Command
from models.commandType import CommandType
from ...displayConstants import COLORS
from .circularButton import CircularButton
from .optionsButton import OptionsButton
from .joyStickButton import JoyStickButton
from .bumperButton import BumperButton
from .triggerButton import TriggerButton
from .touchPadButton import TouchPadButton
from.dpadButton import DPadButton
from redux import store, utils as ReduxUtils
from redux.actions import controllerCoupler as actions

class ControlDisplay(tk.Canvas):

    width = 340
    margin = 5
    widthUnits = 15
    heightUnits = 14

    parameters: List[AppParameter]

    def __init__(self, master=None):
        self.unitSize = (self.width - (2 * self.margin)) / self.widthUnits
        self.height = (self.unitSize * self.heightUnits) + (2 * self.margin)
        super().__init__(master, width=self.width, height=(self.width / self.widthUnits) * self.heightUnits,
                         highlightthickness=0, relief="flat", bg="#000000")
        
        self.master = master
        self.parameters = []
        self.appParameterLength = 0
        self.buttonsCreated = False
        self.chordEngineControlMode = 'internal'

        self.pack(side="top", anchor="nw", padx=(0, 0), pady=(0, 0))

        store.subscribe(self.__handleStoreUpdate)

    def __handleStoreUpdate(self):
        meState = store.get_state()['musicEngine']
        if (meState['controlMode'] != self.chordEngineControlMode):
            self.chordEngineControlMode = meState['controlMode']
            if self.buttonsCreated:
                self.__updateButtonParams()

        state = store.get_state()['controllerCoupler']
        params = state['appParameters']
        controlMap: ControlMap = state['activeControlMap']
        musicEngineParametersLoaded = state['musicEngineAppParametersLoaded']
        if controlMap != None and musicEngineParametersLoaded and len(params) != self.appParameterLength:
            if (not self.buttonsCreated): 
                self.appParameterLength = len(params)
                self.__createButtons(params, controlMap.map)
                self.buttonsCreated = True
                ReduxUtils.addAppParameters(self.parameters)
            else:
                self.appParameterLength = len(params)
                self.__updateButtonParams(params, controlMap.map)

    def __createButtons(self, params, map):
         
        def getParam(key):
            return self.getFirstMEParameter(params, map, key)
         
        self.createMainButtons(getParam)
        self.createStartButton(map, params)
        self.createDpadButtons(getParam)
        self.createOptionsButtons(getParam)
        self.createJoySticks(getParam)
        self.createBumperButtons(getParam)
        self.createTriggerButtons(getParam)
        self.createTouchPadButton(getParam)

    def __updateButtonParams(self, params, map):

        def getParam(key):
            return self.getFirstMEParameter(params, map, key)

        self.southButton.setParam(getParam("SOUTH_BUTTON"))
        self.eastButton.setParam(getParam("EAST_BUTTON"))
        self.northButton.setParam(getParam("NORTH_BUTTON"))
        self.westButton.setParam(getParam("WEST_BUTTON"))


        self.startButton.setParam(self.getStartButtonParam(map, params))

        leftParam, rightParam, upParam, downParam, xType, yType = self.getDPadParams(getParam)

        self.dpadDownButton.setParam(downParam, yType)
        self.dpadUpButton.setParam(upParam, yType)
        self.dpadLeftButton.setParam(leftParam, xType)
        self.dpadRightButton.setParam(rightParam, xType)

        self.leftOptionButton.setParam(getParam("LEFT_OPTION"))
        self.rightOptionButton.setParam(getParam("RIGHT_OPTION"))

        self.leftTriggerButton.setParam(getParam("LEFT_TRIGGER"))
        self.rightTriggerButton.setParam(getParam("RIGHT_TRIGGER"))

        self.leftBumperButton.setParam(getParam("LEFT_BUMPER"))
        self.rightBumperButton.setParam(getParam("RIGHT_BUMPER"))

        self.touchPadButton.setXParam(getParam("TOUCHPAD_X"))
        self.touchPadButton.setYParam(getParam("TOUCHPAD_Y"))

        leftXParams, leftXType = self.getJoystickAxisParams("LEFT_STICK", "X", getParam)
        leftYParams, leftYType = self.getJoystickAxisParams("LEFT_STICK", "Y", getParam)
        rightXParams, rightXType = self.getJoystickAxisParams("RIGHT_STICK", "X", getParam)
        rightYParams, rightYType = self.getJoystickAxisParams("RIGHT_STICK", "Y", getParam)

        self.leftStick.setXParams(leftXParams, leftXType)
        self.leftStick.setYParams(leftYParams, leftYType)
        self.rightStick.setXParams(rightXParams, rightXType)
        self.rightStick.setYParams(rightYParams, rightYType)


    def unitsToCoord(self, units):
        return self.margin + (units * self.unitSize)

    def createMainButtons(self, getParam):
        cX = 12
        cY = 7.75
        uToC = self.unitsToCoord
        self.southButton = CircularButton(self, getParam("SOUTH_BUTTON"), uToC(cX), uToC(cY + 2), self.unitSize)
        self.eastButton = CircularButton(self, getParam("EAST_BUTTON"), uToC(cX + 2), uToC(cY), self.unitSize)
        self.northButton = CircularButton(self, getParam("NORTH_BUTTON"), uToC(cX), uToC(cY - 2), self.unitSize)
        self.westButton = CircularButton(self, getParam("WEST_BUTTON"), uToC(cX - 2), uToC(cY), self.unitSize)
        self.parameters.extend([
            AppParameter(
                validCommandTypes=[CommandType.ON_OFF],
                commandMappings={Command.ON: self.southButton.on, Command.OFF: self.southButton.off},
                key="UI_SOUTH_BUTTON",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                validCommandTypes=[CommandType.ON_OFF],
                commandMappings={Command.ON: self.eastButton.on, Command.OFF: self.eastButton.off},
                key="UI_EAST_BUTTON",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                validCommandTypes=[CommandType.ON_OFF],
                commandMappings={Command.ON: self.northButton.on, Command.OFF: self.northButton.off},
                key="UI_NORTH_BUTTON",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                validCommandTypes=[CommandType.ON_OFF],
                commandMappings={Command.ON: self.westButton.on, Command.OFF: self.westButton.off},
                key="UI_WEST_BUTTON",
                remappable=False,
                type=AppParameterType.UI
            )
        ])

    def createTriggerButtons(self, getParam):
        self.leftTriggerButton = TriggerButton(self, getParam("LEFT_TRIGGER"), 2.5, 0.8)
        self.rightTriggerButton = TriggerButton(self, getParam("RIGHT_TRIGGER"), 12.5, 0.8)  
        self.parameters.extend([
            AppParameter(
                validCommandTypes=[CommandType.ON_OFF],
                commandMappings={Command.ON: self.leftTriggerButton.on, Command.OFF: self.leftTriggerButton.off},
                key="UI_LEFT_TRIGGER",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                validCommandTypes=[CommandType.ON_OFF],
                commandMappings={Command.ON: self.rightTriggerButton.on, Command.OFF: self.rightTriggerButton.off},
                key="UI_RIGHT_TRIGGER",
                remappable=False,
                type=AppParameterType.UI
            )
        ])

    def createBumperButtons(self, getParam):
        self.leftBumperButton = BumperButton(self, getParam("LEFT_BUMPER"), 2.5, 3.25)
        self.rightBumperButton = BumperButton(self, getParam("RIGHT_BUMPER"), 12.5, 3.25)
        self.parameters.extend([
            AppParameter(
                validCommandTypes=[CommandType.ON_OFF],
                commandMappings={Command.ON: self.leftBumperButton.on, Command.OFF: self.leftBumperButton.off},
                key="UI_LEFT_BUMPER",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                validCommandTypes=[CommandType.ON_OFF],
                commandMappings={Command.ON: self.rightBumperButton.on, Command.OFF: self.rightBumperButton.off},
                key="UI_RIGHT_BUMPER",
                label="UI Right Bumper",
                labelAbreviation=None,
                remappable=False,
                type=AppParameterType.UI
            )
        ])

    def createTouchPadButton(self, getParam):
        
        self.touchPadButton = TouchPadButton(self, getParam("TOUCHPAD_X"), getParam("TOUCHPAD_Y"), 7.5, 1.5)
        self.parameters.extend([
            AppParameter(
                validCommandTypes=[CommandType.ANALOG],
                commandMappings={Command.UPDATE: self.touchPadButton.update_x},
                key="UI_TOUCHPAD_X",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                validCommandTypes=[CommandType.ANALOG],
                commandMappings={Command.UPDATE: self.touchPadButton.update_y},
                key="UI_TOUCHPAD_Y",
                remappable=False,
                type=AppParameterType.UI
            )
        ])

    def createStartButton(self, map, params: Dict[str, AppParameter]):
        param = self.getStartButtonParam(map, params)
                
        uToC = self.unitsToCoord

        self.startButton = CircularButton(self, param, uToC(7.5), uToC(9.5), self.unitSize)
        self.parameters.extend([
            AppParameter(
                validCommandTypes=[CommandType.ON_OFF],
                commandMappings={Command.ON: self.startButton.on, Command.OFF: self.startButton.off},
                key="UI_START_BUTTON",
                remappable=False,
                type=AppParameterType.UI
            )
        ])

    def createDpadButtons(self, getParam):

        leftParam, rightParam, upParam, downParam, xType, yType = self.getDPadParams(getParam)

        cx = 3; cy = 7.75
        self.dpadDownButton = DPadButton(self, downParam, yType, "DOWN", cx, cy)
        self.dpadUpButton = DPadButton(self, upParam, yType, "UP", cx, cy)
        self.dpadLeftButton = DPadButton(self, leftParam, xType, "LEFT", cx, cy)
        self.dpadRightButton = DPadButton(self, rightParam, xType, "RIGHT", cx, cy)
        self.parameters.extend([
            AppParameter(
                validCommandTypes=[CommandType.ON_OFF],
                commandMappings={Command.ON: self.dpadDownButton.on, Command.OFF: self.dpadDownButton.off},
                key="UI_DPAD_DOWN",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                validCommandTypes=[CommandType.ON_OFF],
                commandMappings={Command.ON: self.dpadUpButton.on, Command.OFF: self.dpadUpButton.off},
                key="UI_DPAD_UP",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                validCommandTypes=[CommandType.ON_OFF],
                commandMappings={Command.ON: self.dpadLeftButton.on, Command.OFF: self.dpadLeftButton.off},
                key="UI_DPAD_LEFT",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                validCommandTypes=[CommandType.ON_OFF],
                commandMappings={Command.ON: self.dpadRightButton.on, Command.OFF: self.dpadRightButton.off},
                key="UI_DPAD_RIGHT",
                remappable=False,
                type=AppParameterType.UI
            )
        ])

    def createOptionsButtons(self, getParam):
        self.leftOptionButton = OptionsButton(self, getParam("LEFT_OPTION"), 6, 4.75, self.unitSize)
        self.rightOptionButton = OptionsButton(self, getParam("RIGHT_OPTION"), 9, 4.75, self.unitSize)
        self.parameters.extend([
            AppParameter(
                validCommandTypes=[CommandType.ON_OFF],
                commandMappings={Command.ON: self.leftOptionButton.on, Command.OFF: self.leftOptionButton.off},
                key="UI_LEFT_OPTION",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                validCommandTypes=[CommandType.ON_OFF],
                commandMappings={Command.ON: self.rightOptionButton.on, Command.OFF: self.rightOptionButton.off},
                key="UI_RIGHT_OPTION",
                remappable=False,
                type=AppParameterType.UI
            )
        ])

    def createJoySticks(self, getParam):

        leftXParams, leftXType = self.getJoystickAxisParams("LEFT_STICK", "X", getParam)
        leftYParams, leftYType = self.getJoystickAxisParams("LEFT_STICK", "Y", getParam)
        rightXParams, rightXType = self.getJoystickAxisParams("RIGHT_STICK", "X", getParam)
        rightYParams, rightYType = self.getJoystickAxisParams("RIGHT_STICK", "Y", getParam)

        self.leftStick = JoyStickButton(
            self, 
            leftXParams, leftYParams, leftXType, leftYType,
            getParam("LEFT_STICK_BUTTON"),
            5.25, 12, "LEFT")
        
        self.rightStick = JoyStickButton(
            self, 
            rightXParams, rightYParams, rightXType, rightYType,
            getParam("RIGHT_STICK_BUTTON"),
            9.75, 12, "RIGHT")
        self.parameters.extend([
            AppParameter(
                validCommandTypes=[CommandType.ON_OFF],
                commandMappings={Command.ON: self.leftStick.button_on, Command.OFF: self.leftStick.button_off},
                key="UI_LEFT_STICK_BUTTON",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                validCommandTypes=[CommandType.ON_OFF],
                commandMappings={Command.ON: self.leftStick.left_on, Command.OFF: self.leftStick.left_off},
                key="UI_LEFT_STICK_LEFT",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                validCommandTypes=[CommandType.ON_OFF],
                commandMappings={Command.ON: self.leftStick.right_on, Command.OFF: self.leftStick.right_off},
                key="UI_LEFT_STICK_RIGHT",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                validCommandTypes=[CommandType.ON_OFF],
                commandMappings={Command.ON: self.leftStick.up_on, Command.OFF: self.leftStick.up_off},
                key="UI_LEFT_STICK_UP",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                validCommandTypes=[CommandType.ON_OFF],
                commandMappings={Command.ON: self.leftStick.down_on, Command.OFF: self.leftStick.down_off},
                key="UI_LEFT_STICK_DOWN",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                validCommandTypes=[CommandType.ANALOG],
                commandMappings={Command.UPDATE: self.leftStick.update_x},
                key="UI_LEFT_STICK_X",
                remappable=False
            ),
            AppParameter(
                validCommandTypes=[CommandType.ANALOG],
                commandMappings={Command.UPDATE: self.leftStick.update_y},
                key="UI_LEFT_STICK_Y",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                validCommandTypes=[CommandType.ON_OFF],
                commandMappings={Command.ON: self.rightStick.button_on, Command.OFF: self.rightStick.button_off},
                key="UI_RIGHT_STICK_BUTTON",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                validCommandTypes=[CommandType.ON_OFF],
                commandMappings={Command.ON: self.rightStick.left_on, Command.OFF: self.rightStick.left_off},
                key="UI_RIGHT_STICK_LEFT",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                validCommandTypes=[CommandType.ON_OFF],
                commandMappings={Command.ON: self.rightStick.right_on, Command.OFF: self.rightStick.right_off},
                key="UI_RIGHT_STICK_RIGHT",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                validCommandTypes=[CommandType.ON_OFF],
                commandMappings={Command.ON: self.rightStick.up_on, Command.OFF: self.rightStick.up_off},
                key="UI_RIGHT_STICK_UP",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                validCommandTypes=[CommandType.ON_OFF],
                commandMappings={Command.ON: self.rightStick.down_on, Command.OFF: self.rightStick.down_off},
                key="UI_RIGHT_STICK_DOWN",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                validCommandTypes=[CommandType.ANALOG],
                commandMappings={Command.UPDATE: self.rightStick.update_x},
                key="UI_RIGHT_STICK_X",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                validCommandTypes=[CommandType.ANALOG],
                commandMappings={Command.UPDATE: self.rightStick.update_y},
                key="UI_RIGHT_STICK_Y",
                remappable=False,
                type=AppParameterType.UI
            )
        ])

    def getStartButtonParam(self, map, params: Dict[str, AppParameter]):
        param = None
        if ("START_BUTTON" in map):
            for parameterKey in map["START_BUTTON"]:
                if (parameterKey in params):
                    param =  params[parameterKey]
        return param

    def getDPadParams(self, getParam):
        xPolar = getParam("DPAD_X")
        yPolar = getParam("DPAD_Y")
        left = getParam("DPAD_X_LEFT")
        right = getParam("DPAD_X_RIGHT")
        up = getParam("DPAD_Y_UP")
        down = getParam("DPAD_Y_DOWN")

        xType, yType = None, None
        leftParam, rightParam, upParam, downParam = None, None, None, None

        if (xPolar):
            xType = "POLAR"
            leftParam = xPolar
            rightParam = xPolar
        elif (left and right):
            xType = "ON_OFF"
            leftParam = left
            rightParam = right

        if (yPolar):
            yType = "POLAR"
            upParam = yPolar
            downParam = yPolar
        elif (up and down):
            yType = "ON_OFF"
            upParam = up
            downParam = down

        return leftParam, rightParam, upParam, downParam, xType, yType

    def getJoystickAxisParams(self, prefix: str, axis: str, getParam):
        positiveSuffix = "RIGHT" if axis == "X" else "UP"
        negativeSuffix = "LEFT" if axis == "X" else "DOWN"

        pParam = getParam(f"{prefix}_{axis}_{positiveSuffix}")
        nParam = getParam(f"{prefix}_{axis}_{negativeSuffix}")
        polarParam = getParam(f"{prefix}_{axis}_POLAR")
        analogParam = getParam(f"{prefix}_{axis}")

        if analogParam:
            return [analogParam], "ANALOG"
        elif polarParam:
            return [polarParam], "POLAR"
        elif nParam and pParam:
            return [nParam, pParam], "ON_OFF"
        else:
            return [], None

    def getFirstMEParameter(self, params: Dict[str, AppParameter], map: Dict[str, List[str]], key):
        if (key in map):
            for parameterKey in map[key]:
                parameterType = params[parameterKey].type
                if (parameterKey in params and params[parameterKey].type != AppParameterType.UI):
                    if self.chordEngineControlMode == 'internal' and parameterType == AppParameterType.INTERNAL_CHORD_ENGINE:
                        return params[parameterKey]
                    elif self.chordEngineControlMode == 'external' and parameterType == AppParameterType.EXTERNAL_CHORD_ENGINE:
                        return params[parameterKey]
            
        return None