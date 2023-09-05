import tkinter as tk
from controllerManager.maps.me.controlAbreviations import controlAbreviations as CONTROL_ABREVIATIONS
from ...displayConstants import COLORS
from .circularButton import CircularButton
from .optionsButton import OptionsButton
from .joyStickButton import JoyStickButton
from.dpadButton import DPadButton
from redux import store, utils as ReduxUtils

class ControlDisplay(tk.Canvas):

    width = 320
    margin = 5
    widthUnits = 15
    heightUnits = 15

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
        meMap = ReduxUtils.getActiveMeMap()
        uiMap = ReduxUtils.getActiveUiMap()
        if meMap != None and uiMap != None and not self.ControllerConnected:
            abrevs = CONTROL_ABREVIATIONS
            self.ControllerConnected = True
            self.createMainButtons(meMap, abrevs)
            self.createStartButton(uiMap, abrevs)
            self.createDpadButtons(meMap, abrevs)
            self.createOptionsButtons(meMap, abrevs)
            self.createJoySticks(meMap, abrevs)

    def unitsToCoord(self, units):
        return self.margin + (units * self.unitSize)

    def createMainButtons(self, meMap, abrevs):
        cX = 12
        cY = 9
        uToC = self.unitsToCoord
        self.southButton = CircularButton(self, abrevs[meMap["SOUTH_BUTTON_DOWN"]], uToC(cX), uToC(cY + 2), self.unitSize)
        self.eastButton = CircularButton(self, abrevs[meMap["EAST_BUTTON_DOWN"]], uToC(cX + 2), uToC(cY), self.unitSize)
        self.northButton = CircularButton(self, abrevs[meMap["NORTH_BUTTON_DOWN"]], uToC(cX), uToC(cY - 2), self.unitSize)
        self.westButton = CircularButton(self, abrevs[meMap["WEST_BUTTON_DOWN"]], uToC(cX - 2), uToC(cY), self.unitSize)

    def createStartButton(self, uiMap, abrevs):
        uToC = self.unitsToCoord
        cX = uToC(7.5)
        cY = uToC(11)
        self.startButton = CircularButton(self, abrevs[uiMap["START_BUTTON_DOWN"]], cX, cY, self.unitSize)

    def createDpadButtons(self, meMap, abrevs):
        self.dpadDownButton = DPadButton(self, abrevs[meMap["DPAD_DOWN"]], "DOWN", self.unitSize)
        self.dpadUpButton = DPadButton(self, abrevs[meMap["DPAD_UP"]], "UP", self.unitSize)
        self.dpadLeftButton = DPadButton(self, abrevs[meMap["DPAD_LEFT"]], "LEFT", self.unitSize)
        self.dpadRightButton = DPadButton(self, abrevs[meMap["DPAD_RIGHT"]], "RIGHT", self.unitSize)

    def createOptionsButtons(self, meMap, abrevs):
        self.leftOptionButton = OptionsButton(self, abrevs[meMap["LEFT_OPTION_DOWN"]], 6, 6, self.unitSize)
        self.rightOptionButton = OptionsButton(self, abrevs[meMap["RIGHT_OPTION_DOWN"]], 9, 6, self.unitSize)

    def createJoySticks(self, meMap, abrevs):
        self.leftStick = JoyStickButton(self, abrevs[meMap["LEFT_STICK_LEFT"]], abrevs[meMap["LEFT_STICK_RIGHT"]], abrevs[meMap["LEFT_STICK_UP"]], abrevs[meMap["LEFT_STICK_DOWN"]], 5.5, 13)
        self.rightStick = JoyStickButton(self, abrevs[meMap["RIGHT_STICK_LEFT"]], abrevs[meMap["RIGHT_STICK_RIGHT"]], abrevs[meMap["RIGHT_STICK_UP"]], abrevs[meMap["RIGHT_STICK_DOWN"]], 10, 13)

        # self.controls = { 

        #     "DPAD_LEFT": abrevs[meMap["DPAD_LEFT"]],
        #     "DPAD_RIGHT": abrevs[meMap["DPAD_RIGHT"]],
        #     "DPAD_UP": abrevs[meMap["DPAD_UP"]],
        #     "DPAD_DOWN": abrevs[meMap["DPAD_DOWN"]],

        #     "LEFT_STICK_UP": abrevs[meMap["LEFT_STICK_UP"]],
        #     "LEFT_STICK_DOWN": abrevs[meMap["LEFT_STICK_DOWN"]],
        #     "LEFT_STICK_RIGHT": abrevs[meMap["LEFT_STICK_RIGHT"]],
        #     "LEFT_STICK_LEFT": abrevs[meMap["LEFT_STICK_LEFT"]],

        #     "RIGHT_STICK_UP": abrevs[meMap["RIGHT_STICK_UP"]],
        #     "RIGHT_STICK_DOWN": abrevs[meMap["RIGHT_STICK_DOWN"]],
        #     "RIGHT_STICK_RIGHT": abrevs[meMap["RIGHT_STICK_RIGHT"]],
        #     "RIGHT_STICK_LEFT": abrevs[meMap["RIGHT_STICK_LEFT"]],

        #     "RIGHT_BUMPER": abrevs[meMap["RIGHT_BUMPER_DOWN"]],
        #     "LEFT_BUMPER": abrevs[meMap["LEFT_BUMPER_DOWN"]],
        #     "RIGHT_TRIGGER": abrevs[meMap["RIGHT_TRIGGER_DOWN"]],
        #     "LEFT_TRIGGER": abrevs[meMap["LEFT_TRIGGER_DOWN"]],

        #     "LEFT_OPTION": abrevs[meMap["LEFT_OPTION_DOWN"]],
        #     "RIGHT_OPTION": abrevs[meMap["RIGHT_OPTION_DOWN"]],

        #     "RIGHT_STICK_BUTTON": abrevs[meMap["RIGHT_STICK_BUTTON_DOWN"]],
        #     "LEFT_STICK_BUTTON": abrevs[meMap["LEFT_STICK_BUTTON_DOWN"]],

        #     "TOUCHPAD_X": abrevs[meMap["TOUCHPAD_X_UPDATE"]],
        #     "TOUCHPAD_Y": abrevs[meMap["TOUCHPAD_Y_UPDATE"]],
        # }

        