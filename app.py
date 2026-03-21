import asyncio

from controller_coupler import ControllerCoupler
from controller_manager import ControllerManager
from display import Display
from music_engine import MusicEngine
from redux.settings_storage import settings_storage_utility


class App:

    controller_manager: ControllerManager
    controller_coupler: ControllerCoupler
    music_engine: MusicEngine
    display: Display

    def __init__(self, args):
        self.use_display = args.display
        if (self.use_display):
            self.display = Display()
        self.controller_manager = ControllerManager()
        self.controller_coupler = ControllerCoupler()
        self.music_engine = MusicEngine()

        self.controller_manager.subscribe(self.controller_coupler.event_handler)


    def start(self):
        settings_storage_utility.load_settings()

        if (self.use_display):
            self.display.start()
        self.music_engine.start()
        self.controller_manager.start()

        asyncio.get_event_loop().run_forever()
