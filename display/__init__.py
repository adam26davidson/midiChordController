from constants import FULLSCREEN, ANIMATION_STEP
from redux import store
from redux.actions import display as actions
from .performFrame import PerformFrame
from .settingsMenu import SettingsMenuFrame
from .settingsPages.midiSettings import MidiSettingsFrame
from .settingsPages.strumSettings import StrumSettingsFrame
from pyrsistent import thaw
import asyncio
import tkinter as tk


class Display():
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

        self.frames["STRUM"] = StrumSettingsFrame(self.root)
        self.frames["MIDI"] = MidiSettingsFrame(self.root)
        self.frames["MENU"] = SettingsMenuFrame(self.root)
        self.frames["PERFORM"] = PerformFrame(self.root)

        store.subscribe(self.__handleStoreUpdate)

    def start(self):
        asyncio.ensure_future(self.__mainLoop())

    async def __mainLoop(self):
        while True:
            if self.state.activeFrame == 'PERFORM':     
                self.frames["PERFORM"].updateFrame()
            self.root.update()
            await asyncio.sleep(ANIMATION_STEP)

    def controllerEventHandler(self, event):
        controllers = store.get_state()['controllerManager']['controllers']
        uiMap = None
        for controller in controllers:
            if controller['role'] == 'primary':
                uiMap = controller['uiMap']['map']
                
        if (event['name'] in uiMap.keys()):
            command = uiMap[event['name']]
            if (command in self.commandMap.keys()):
                self.commandMap[command]()

        if self.state.activeFrame == 'PERFORM':  
            self.frames["PERFORM"].handleControllerEvent(event)

    def __handleStoreUpdate(self):
        state = store.get_state()
        displayState = thaw(state['display'])
        if (displayState['activeFrame'] != self.state.activeFrame):
            if (displayState['activeFrame'] in self.frames.keys()):
                self.state.activeFrame = displayState['activeFrame']
                self.frames[displayState['activeFrame']].tkraise()
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


class DisplayState():
    activeFrame = "PERFORM"
