import tkinter as tk
from controllerManager.maps.me.controlAbreviations import controlAbreviations as CONTROL_ABREVIATIONS
from ...displayConstants import COLORS
from .circularButton import CircularButton
from.dpadButton import DPadButton
from redux import store, utils as ReduxUtils

class ControlDisplay(tk.Canvas):

    width = 300

    def __init__(self, master=None):
        super().__init__(master, width=40, height=370,
                         highlightthickness=0, relief="flat", bg="#000000")
        
        self.unitSize = self.width / 15
        self.height = self.unitSize * 14
        
        self.master = master

        self.ControllerConnected = False
        meMap = ReduxUtils.getActiveMeMap()
        abrevs = CONTROL_ABREVIATIONS
        
        if meMap != None:
            self.ControllerConnected = True
            self.createMainButtons(meMap, abrevs)
            self.createStartButton(meMap, abrevs)
            self.createDpadButtons(meMap, abrevs)
            #self.createJoySticks(meMap, abrevs)

        self.pack(side="top", anchor="nw", padx=(20, 20), pady=(20, 20))

        store.subscribe(self.__handleStoreUpdate)

    def __handleStoreUpdate(self):
        meMap = ReduxUtils.getActiveMeMap()
        if meMap != None:
            abrevs = CONTROL_ABREVIATIONS
            self.ControllerConnected = True
            self.createMainButtons(meMap, abrevs)
            self.createStartButton(meMap, abrevs)
            self.createDpadButtons(meMap, abrevs)
            #self.createJoySticks(meMap, abrevs)

    def createMainButtons(self, meMap, abrevs):

        centerX = self.unitSize * 12
        centerY = self.unitSize * 9
        self.southButton = CircularButton(self, abrevs[meMap["SOUTH_BUTTON_DOWN"]], centerX, centerY + 2, self.unitSize)
        self.eastButton = CircularButton(self, abrevs[meMap["EAST_BUTTON_DOWN"]], centerX + 2, centerY, self.unitSize)
        self.northButton = CircularButton(self, abrevs[meMap["NORTH_BUTTON_DOWN"]], centerX, centerY - 2, self.unitSize)
        self.westButton = CircularButton(self, abrevs[meMap["WEST_BUTTON_DOWN"]], centerX - 2, centerY, self.unitSize)

    def createStartButton(self, meMap, abrevs):
            
        centerX = self.unitSize * 7.5
        centerY = self.unitSize * 11
        #self.startButton = CircularButton(self, abrevs[meMap["START_BUTTON_DOWN"]], centerX, centerY, self.unitSize)

    def createDpadButtons(self, meMap, abrevs):
        self.dpadDownButton = DPadButton(self, abrevs[meMap["DPAD_DOWN"]], "DOWN", self.unitSize)
        self.dpadUpButton = DPadButton(self, abrevs[meMap["DPAD_UP"]], "UP", self.unitSize)
        self.dpadLeftButton = DPadButton(self, abrevs[meMap["DPAD_LEFT"]], "LEFT", self.unitSize)
        self.dpadRightButton = DPadButton(self, abrevs[meMap["DPAD_RIGHT"]], "RIGHT", self.unitSize)

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

        