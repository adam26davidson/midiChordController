import tkinter as tk
from controllerManager.maps.me.controlAbreviations import controlAbreviations as CONTROL_ABREVIATIONS
from ...displayConstants import COLORS
from .circularButton import CircularButton
from .optionsButton import OptionsButton
from .joyStickButton import JoyStickButton
from .bumperButton import BumperButton
from .triggerButton import TriggerButton
from .touchPadButton import TouchPadButton
from.dpadButton import DPadButton
from redux import store, utils as ReduxUtils

class ControlDisplay(tk.Canvas):

    width = 340
    margin = 5
    widthUnits = 15
    heightUnits = 14

    def __init__(self, master=None):
        self.unitSize = (self.width - (2 * self.margin)) / self.widthUnits
        self.height = (self.unitSize * self.heightUnits) + (2 * self.margin)
        super().__init__(master, width=self.width, height=(self.width / self.widthUnits) * self.heightUnits,
                         highlightthickness=0, relief="flat", bg="#000000")
        
        self.master = master
        self.ControllerConnected = False

        self.pack(side="top", anchor="nw", padx=(0, 0), pady=(0, 0))

        store.subscribe(self.__handleStoreUpdate)

    def __handleStoreUpdate(self):
        state = store.get_state()['controllerCoupler']
        params = state['appParameters']
        map = state['activeControlMap']
        if map != None and params != None and not self.ControllerConnected:
            self.ControllerConnected = True
            self.createMainButtons(map, params)
            self.createStartButton(map, params)
            self.createDpadButtons(map, params)
            self.createOptionsButtons(map, params)
            self.createJoySticks(map, params)
            self.createBumperButtons(map, params)
            self.createTriggerButtons(map, params)
            self.createTouchPadButton(map, params)

    def unitsToCoord(self, units):
        return self.margin + (units * self.unitSize)
    
    def createMainButtons(self, map, params):
        cX = 12
        cY = 8
        uToC = self.unitsToCoord
        self.southButton = CircularButton(self, params[map["SOUTH_BUTTON"]], uToC(cX), uToC(cY + 2), self.unitSize)
        self.eastButton = CircularButton(self, params[map["EAST_BUTTON"]], uToC(cX + 2), uToC(cY), self.unitSize)
        self.northButton = CircularButton(self, params[map["NORTH_BUTTON"]], uToC(cX), uToC(cY - 2), self.unitSize)
        self.westButton = CircularButton(self, params[map["WEST_BUTTON"]], uToC(cX - 2), uToC(cY), self.unitSize)

    def createTriggerButtons(self, map, params):
        self.leftTriggerButton = TriggerButton(self, params[map["LEFT_TRIGGER"]], 2.5, 0.875)
        self.rightTriggerButton = TriggerButton(self, params[map["RIGHT_TRIGGER"]], 12.5, 0.875)  

    def createBumperButtons(self, map, params):
        self.leftBumperButton = BumperButton(self, params[map["LEFT_BUMPER"]], 2.5, 3.5)
        self.rightBumperButton = BumperButton(self, params[map["RIGHT_BUMPER"]], 12.5, 3.5)

    def createTouchPadButton(self, map, params):
        self.touchPadButton = TouchPadButton(self, params[map["TOUCHPAD_X"]], params[map["TOUCHPAD_Y"]], 7.5, 1.5)

    def createStartButton(self, map, params):
        uToC = self.unitsToCoord
        self.startButton = CircularButton(self, params[map["START_BUTTON"]], uToC(7.5), uToC(9.75), self.unitSize)

    def createDpadButtons(self, map, params):
        cx = 3; cy = 8
        self.dpadDownButton = DPadButton(self, params[map["DPAD_DOWN"]], "DOWN", cx, cy)
        self.dpadUpButton = DPadButton(self, params[map["DPAD_UP"]], "UP", cx, cy)
        self.dpadLeftButton = DPadButton(self, params[map["DPAD_LEFT"]], "LEFT", cx, cy)
        self.dpadRightButton = DPadButton(self, params[map["DPAD_RIGHT"]], "RIGHT", cx, cy)

    def createOptionsButtons(self, map, params):
        self.leftOptionButton = OptionsButton(self, params[map["LEFT_OPTION"]], 6, 5, self.unitSize)
        self.rightOptionButton = OptionsButton(self, params[map["RIGHT_OPTION"]], 9, 5, self.unitSize)

    def createJoySticks(self, map, params):

        self.leftStick = JoyStickButton(
            self, 
            params[map["LEFT_STICK_LEFT"]], 
            params[map["LEFT_STICK_RIGHT"]], 
            params[map["LEFT_STICK_UP"]], 
            params[map["LEFT_STICK_DOWN"]], 
            params[map["LEFT_STICK_BUTTON_DOWN"]],
            5.25, 12.25, "LEFT")
        
        self.rightStick = JoyStickButton(
            self, 
            params[map["RIGHT_STICK_LEFT"]], 
            params[map["RIGHT_STICK_RIGHT"]], 
            params[map["RIGHT_STICK_UP"]], 
            params[map["RIGHT_STICK_DOWN"]], 
            params[map["RIGHT_STICK_BUTTON_DOWN"]],
            9.75, 12.25, "RIGHT")

        