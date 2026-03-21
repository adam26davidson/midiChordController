import asyncio
import tkinter as tk

from pyrsistent import thaw

from constants import ANIMATION_STEP, FULLSCREEN
from models.app_parameter import AppParameter
from models.command import Command
from models.command_type import CommandType
from redux import store
from redux import utils as redux_utils
from redux.actions import display as actions

from .perform.perform_frame import PerformFrame
from .settings_menu import SettingsMenuFrame
from .settings_pages.chord_settings import ChordSettingsFrame
from .settings_pages.midi_settings import MidiSettingsFrame
from .settings_pages.strum_settings import StrumSettingsFrame


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

        self.command_map = {
            "MENU": self.toggle_menu
        }

        self.frames = {}

        self.frames["CHORD"] = ChordSettingsFrame(self.root)
        self.frames["STRUM"] = StrumSettingsFrame(self.root)
        self.frames["MIDI"] = MidiSettingsFrame(self.root)
        self.frames["MENU"] = SettingsMenuFrame(self.root)
        self.frames["PERFORM"] = PerformFrame(self.root)

        redux_utils.add_app_parameters(self.get_parameters())

        store.subscribe(self.__handle_store_update)

    def start(self):
        _task = asyncio.ensure_future(self.__main_loop())

    async def __main_loop(self):
        _display_loop_count = 0
        while True:
            if self.state.active_frame == 'PERFORM':
                self.frames["PERFORM"].update_frame()
            self.root.update_idletasks()
            self.root.update()
            _display_loop_count += 1
            if _display_loop_count % 30 == 0:
                print(f"[DISPLAY] heartbeat (loop #{_display_loop_count})", flush=True)
            await asyncio.sleep(ANIMATION_STEP)

    def controller_event_handler(self, event):
        controllers = store.get_state()['controllerManager']['controllers']
        ui_map = None
        for controller in controllers:
            if controller['role'] == 'primary':
                ui_map = controller['uiMap']['map']

        if ui_map is not None and (event['name'] in ui_map):
            command = ui_map[event['name']]
            if (command in self.command_map):
                self.command_map[command]()

        if self.state.active_frame == 'PERFORM':
            self.frames["PERFORM"].handle_controller_event(event)

    def get_parameters(self):
        return [
            AppParameter(
                valid_command_types=[CommandType.TOGGLE],
                command_mappings={Command.TOGGLE: self.toggle_menu},
                key="MENU",
                label="Menu",
                label_abreviation="☰",
                remappable=False
            )
        ]


    def __handle_store_update(self):
        state = store.get_state()
        display_state = thaw(state['display'])
        if (display_state['activeFrame'] != self.state.active_frame):
            if (display_state['activeFrame'] in self.frames):
                self.state.active_frame = display_state['activeFrame']
                self.root.after(0, lambda: self.frames[display_state['activeFrame']].tkraise())
            else:
                store.dispatch(actions.change_active_frame(self.state.active_frame))

    def toggle_menu(self):
        if (self.state.active_frame == "MENU"):
            self.state.active_frame = "PERFORM"
            self.frames["PERFORM"].tkraise()
        else:
            self.state.active_frame = "MENU"
            self.frames["MENU"].tkraise()

        store.dispatch(actions.change_active_frame(self.state.active_frame))


class DisplayState:
    active_frame = "PERFORM"
