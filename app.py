import asyncio
from display import Display
from musicEngine import MusicEngine
from controllerManager import ControllerManager
from redux.settingsStorage import settingsStorageUtility


class App():

    def __init__(self, args):
        self.useDisplay = args.display
        if (self.useDisplay):
            self.display = Display()
        self.controllerManager = ControllerManager()
        self.musicEngine = MusicEngine()

        self.controllerManager.subscribe(
            self.musicEngine.controllerEventHandler)
        if (self.useDisplay):
            self.controllerManager.subscribe(
                self.display.controllerEventHandler)
        

    def start(self):
        if (self.useDisplay):
            self.display.start()
        self.musicEngine.start()
        self.controllerManager.start()

        settingsStorageUtility.loadSettings()
        
        asyncio.get_event_loop().run_forever()
