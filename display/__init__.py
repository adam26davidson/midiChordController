import asyncio
import time
import tkinter as tk

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

        self._dirty = False
        self._settings_frames = {'CHORD', 'STRUM', 'MIDI'}
        store.subscribe(self.__handle_store_update)

    def start(self):
        _task = asyncio.ensure_future(self.__main_loop())

    async def __main_loop(self):
        _display_loop_count = 0
        _last_frame_end = time.monotonic()
        _total_work_ms = 0.0
        _total_frame_ms = 0.0
        _max_work_ms = 0.0
        _max_frame_ms = 0.0
        _slow_frames = 0
        while True:
            frame_start = time.monotonic()
            frame_gap_ms = (frame_start - _last_frame_end) * 1000

            self._check_state()
            if self.state.active_frame == 'PERFORM':
                self.frames["PERFORM"].check_state()
                self.frames["PERFORM"].update_frame()
            elif self.state.active_frame in self._settings_frames:
                self.frames[self.state.active_frame].check_state()
            self.root.update_idletasks()
            self.root.update()

            now = time.monotonic()
            work_ms = (now - frame_start) * 1000
            total_frame_ms = (now - _last_frame_end) * 1000
            _last_frame_end = now

            _total_work_ms += work_ms
            _total_frame_ms += total_frame_ms
            _max_work_ms = max(_max_work_ms, work_ms)
            _max_frame_ms = max(_max_frame_ms, total_frame_ms)
            _display_loop_count += 1

            if total_frame_ms > 20:
                _slow_frames += 1
                print(f"[DISPLAY] SLOW frame #{_display_loop_count}: "
                      f"work={work_ms:.1f}ms total={total_frame_ms:.1f}ms "
                      f"gap={frame_gap_ms:.1f}ms", flush=True)

            if _display_loop_count % 60 == 0:
                avg_work = _total_work_ms / 60
                avg_frame = _total_frame_ms / 60
                fps = 1000 / avg_frame if avg_frame > 0 else 0
                print(f"[DISPLAY] fps={fps:.1f} "
                      f"avg_work={avg_work:.1f}ms avg_frame={avg_frame:.1f}ms "
                      f"max_work={_max_work_ms:.1f}ms max_frame={_max_frame_ms:.1f}ms "
                      f"slow={_slow_frames}/60", flush=True)
                _total_work_ms = 0.0
                _total_frame_ms = 0.0
                _max_work_ms = 0.0
                _max_frame_ms = 0.0
                _slow_frames = 0

            elapsed = now - frame_start
            await asyncio.sleep(max(0, ANIMATION_STEP - elapsed))

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
        self._dirty = True

    def _check_state(self):
        if not self._dirty:
            return
        self._dirty = False
        state = store.get_state()
        display_state = state['display']
        if (display_state['activeFrame'] != self.state.active_frame):
            if (display_state['activeFrame'] in self.frames):
                self.state.active_frame = display_state['activeFrame']
                self.frames[display_state['activeFrame']].tkraise()
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
