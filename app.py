import asyncio
from controllerCoupler import ControllerCoupler
from display import Display
from musicEngine import MusicEngine
from controllerManager import ControllerManager
from redux.settingsStorage import settingsStorageUtility


class App():

    controllerManager: ControllerManager
    controllerCoupler: ControllerCoupler
    musicEngine: MusicEngine
    display: Display

    def __init__(self, args):
        self.useDisplay = args.display
        if (self.useDisplay):
            self.display = Display()
        self.controllerManager = ControllerManager()
        self.controllerCoupler = ControllerCoupler()
        self.musicEngine = MusicEngine()

        self.controllerCoupler.setControlsGetter(self.controllerManager.getControls)
        self.controllerManager.subscribe(self.controllerCoupler.eventHandler)
        

    def start(self):
        if (self.useDisplay):
            self.display.start()
        self.musicEngine.start()
        self.controllerManager.start()

        settingsStorageUtility.loadSettings()
        
        asyncio.get_event_loop().run_forever()
