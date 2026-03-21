import asyncio
import tkinter as tk

from pyrsistent import thaw

from constants import ANIMATION_STEP, FULLSCREEN
from models.appParameter import AppParameter
from models.command import Command
from models.commandType import CommandType
from redux import store
from redux import utils as reduxUtils
from redux.actions import display as actions

from .perform.performFrame import PerformFrame
from .settingsMenu import SettingsMenuFrame
from .settingsPages.chordSettings import ChordSettingsFrame
from .settingsPages.midiSettings import MidiSettingsFrame
from .settingsPages.strumSettings import StrumSettingsFrame


class Display:
    def __init__(self):
        self.root = tk.Tk()

        self.root.overrideredirect(True)
        self.root.overrideredirect(False)
        self.root['cursor'] = 'none'

        if FULLSCREEN:
            self.root.attributes("-fullscreen", True)
            self.root.wm_attributes("-topmost", 1)
            self.root.focus_set()
        else:
            self.root.geometry("800x480")

        def close_escape(event=None):
            print("escaped")
            self.root.destroy()

        self.root.bind("<Escape>", close_escape)
        self.root.configure(bg='black')

        self.state = DisplayState()

        self.commandMap = {
            "MENU": self.toggleMenu
        }

        self.frames = {}

        self.frames["CHORD"] = ChordSettingsFrame(self.root)
        self.frames["STRUM"] = StrumSettingsFrame(self.root)
        self.frames["MIDI"] = MidiSettingsFrame(self.root)
        self.frames["MENU"] = SettingsMenuFrame(self.root)
        self.frames["PERFORM"] = PerformFrame(self.root)

        reduxUtils.addAppParameters(self.getParameters())

        store.subscribe(self.__handleStoreUpdate)

    def start(self):
        _task = asyncio.ensure_future(self.__mainLoop())

    async def __mainLoop(self):
        _displayLoopCount = 0
        while True:
            if self.state.activeFrame == 'PERFORM':
                self.frames["PERFORM"].updateFrame()
            self.root.update_idletasks()
            self.root.update()
            _displayLoopCount += 1
            if _displayLoopCount % 30 == 0:
                print(f"[DISPLAY] heartbeat (loop #{_displayLoopCount})", flush=True)
            await asyncio.sleep(ANIMATION_STEP)

    def controllerEventHandler(self, event):
        controllers = store.get_state()['controllerManager']['controllers']
        uiMap = None
        for controller in controllers:
            if controller['role'] == 'primary':
                uiMap = controller['uiMap']['map']

        if (event['name'] in uiMap):
            command = uiMap[event['name']]
            if (command in self.commandMap):
                self.commandMap[command]()

        if self.state.activeFrame == 'PERFORM':
            self.frames["PERFORM"].handleControllerEvent(event)

    def getParameters(self):
        return [
            AppParameter(
                validCommandTypes=[CommandType.TOGGLE],
                commandMappings={Command.TOGGLE: self.toggleMenu},
                key="MENU",
                label="Menu",
                labelAbreviation="☰",
                remappable=False
            )
        ]


    def __handleStoreUpdate(self):
        state = store.get_state()
        displayState = thaw(state['display'])
        if (displayState['activeFrame'] != self.state.activeFrame):
            if (displayState['activeFrame'] in self.frames):
                self.state.activeFrame = displayState['activeFrame']
                self.root.after(0, lambda: self.frames[displayState['activeFrame']].tkraise())
            else:
                store.dispatch(actions.changeActiveFrame(self.state.activeFrame))

    def toggleMenu(self):
        if (self.state.activeFrame == "MENU"):
            self.state.activeFrame = "PERFORM"
            self.frames["PERFORM"].tkraise()
        else:
            self.state.activeFrame = "MENU"
            self.frames["MENU"].tkraise()

        store.dispatch(actions.changeActiveFrame(self.state.activeFrame))


class DisplayState:
    activeFrame = "PERFORM"
