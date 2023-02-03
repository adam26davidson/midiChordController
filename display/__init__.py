from constants import FULLSCREEN, ANIMATION_STEP
from redux import store
from .performFrame import PerformFrame
from pyrsistent import thaw
import asyncio
import tkinter as tk


class Display():
    def __init__(self):
        self.height = 480
        self.width = 800
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

        self.state = {
            
        }

        self.performFrame = PerformFrame(self.root)

    def start(self):
        asyncio.ensure_future(self.__mainLoop())

    async def __mainLoop(self):
        while True:
            self.performFrame.updateFrame()
            self.root.update()
            await asyncio.sleep(ANIMATION_STEP)

    def controllerEventHandler(self, event):
        controllers = store.get_state()['controllerManager']['controllers']
        for controller in controllers:
            if controller['role'] == 'primary':
                uiMap = controller['uiMap']['map']
        #if uiMap:

        self.performFrame.handleControllerEvent(event)
