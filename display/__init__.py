from __future__ import annotations

import asyncio
import logging
import time
import tkinter as tk
from typing import Callable, cast

from constants import ANIMATION_STEP, FULLSCREEN
from models.app_parameter import AppParameter
from models.command import Command
from models.command_type import CommandType
from redux import get_controller_manager_state, get_display_state, store
from redux import utils as redux_utils
from redux.actions import display as actions

from .perform.perform_frame import PerformFrame
from .settings_menu import SettingsMenuFrame
from .settings_pages.chord_settings import ChordSettingsFrame
from .settings_pages.midi_settings import MidiSettingsFrame
from .settings_pages.strum_settings import StrumSettingsFrame

logger = logging.getLogger(__name__)


FULLSCREEN_RETRY_ATTEMPTS = 5
FULLSCREEN_RETRY_DELAY_MS = 500


class Display:
    def __init__(self) -> None:
        self.root = tk.Tk()

        self.root.overrideredirect(True)
        self.root.overrideredirect(False)
        self.root['cursor'] = 'none'

        if FULLSCREEN:
            self._apply_fullscreen()
        else:
            self.root.geometry("800x480")

        def close_escape(event: object = None) -> None:
            logger.debug("escaped")
            self.root.destroy()

        self.root.bind("<Escape>", close_escape)
        self.root.configure(bg='black')

        self.state = DisplayState()

        self.command_map: dict[str, Callable[[], None]] = {
            "MENU": self.toggle_menu
        }

        self.frames: dict[str, tk.Frame] = {}

        self.chord_settings = ChordSettingsFrame(self.root)
        self.strum_settings = StrumSettingsFrame(self.root)
        self.midi_settings = MidiSettingsFrame(self.root)
        self.menu_frame = SettingsMenuFrame(self.root)
        self.perform_frame = PerformFrame(self.root)

        self.frames["CHORD"] = self.chord_settings
        self.frames["STRUM"] = self.strum_settings
        self.frames["MIDI"] = self.midi_settings
        self.frames["MENU"] = self.menu_frame
        self.frames["PERFORM"] = self.perform_frame

        redux_utils.add_app_parameters(self.get_parameters())

        self._dirty: bool = False
        self._fullscreen_retries: int = 0
        self._settings_frames: set[str] = {'CHORD', 'STRUM', 'MIDI'}
        store.subscribe(self.__handle_store_update)

    def _apply_fullscreen(self) -> None:
        """Apply fullscreen with retry logic for Wayland/Xwayland compositors.

        On fast restarts the compositor may not have released the previous
        fullscreen window yet, causing the new window to open in windowed mode.
        This retries fullscreen with delays to handle that race condition.
        """
        self.root.attributes("-fullscreen", True)
        self.root.wm_attributes("-topmost", 1)
        self.root.focus_set()
        self._fullscreen_retries = 0
        self.root.after(FULLSCREEN_RETRY_DELAY_MS, self._check_fullscreen)

    def _check_fullscreen(self) -> None:
        """Verify fullscreen took effect by checking window size vs screen size."""
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        win_w = self.root.winfo_width()
        win_h = self.root.winfo_height()

        if win_w >= screen_w and win_h >= screen_h:
            logger.info("Fullscreen confirmed (%dx%d)", win_w, win_h)
            return

        self._fullscreen_retries += 1
        if self._fullscreen_retries >= FULLSCREEN_RETRY_ATTEMPTS:
            logger.warning(
                "Fullscreen failed after %d attempts (window: %dx%d, screen: %dx%d)",
                FULLSCREEN_RETRY_ATTEMPTS, win_w, win_h, screen_w, screen_h,
            )
            return

        logger.info(
            "Fullscreen not yet active (attempt %d, window: %dx%d), retrying...",
            self._fullscreen_retries, win_w, win_h,
        )
        self.root.attributes("-fullscreen", False)
        self.root.update_idletasks()
        self.root.attributes("-fullscreen", True)
        self.root.wm_attributes("-topmost", 1)
        self.root.focus_set()
        self.root.after(FULLSCREEN_RETRY_DELAY_MS, self._check_fullscreen)

    def start(self) -> None:
        _task = asyncio.ensure_future(self.__main_loop())

    async def __main_loop(self) -> None:
        _display_loop_count: int = 0
        _last_frame_end: float = time.monotonic()
        _total_work_ms: float = 0.0
        _total_frame_ms: float = 0.0
        _max_work_ms: float = 0.0
        _max_frame_ms: float = 0.0
        _slow_frames: int = 0
        while True:
            frame_start = time.monotonic()
            frame_gap_ms = (frame_start - _last_frame_end) * 1000

            self._check_state()
            if self.state.active_frame == 'PERFORM':
                self.perform_frame.check_state()
                self.perform_frame.update_frame()
            elif self.state.active_frame == 'CHORD':
                self.chord_settings.check_state()
            elif self.state.active_frame == 'STRUM':
                self.strum_settings.check_state()
            elif self.state.active_frame == 'MIDI':
                self.midi_settings.check_state()
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
                logger.debug("[DISPLAY] SLOW frame #%d: work=%.1fms total=%.1fms gap=%.1fms",
                             _display_loop_count, work_ms, total_frame_ms, frame_gap_ms)

            if _display_loop_count % 60 == 0:
                avg_work = _total_work_ms / 60
                avg_frame = _total_frame_ms / 60
                fps = 1000 / avg_frame if avg_frame > 0 else 0
                logger.debug("[DISPLAY] fps=%.1f avg_work=%.1fms avg_frame=%.1fms "
                             "max_work=%.1fms max_frame=%.1fms slow=%d/60",
                             fps, avg_work, avg_frame, _max_work_ms, _max_frame_ms, _slow_frames)
                _total_work_ms = 0.0
                _total_frame_ms = 0.0
                _max_work_ms = 0.0
                _max_frame_ms = 0.0
                _slow_frames = 0

            elapsed = now - frame_start
            await asyncio.sleep(max(0, ANIMATION_STEP - elapsed))

    def controller_event_handler(self, event: dict[str, object]) -> None:
        controllers = get_controller_manager_state()['controllers']
        ui_map = None
        for controller in controllers:
            if controller['role'] == 'primary':
                ui_map_obj = controller['uiMap']
                if ui_map_obj is not None:
                    ui_map = ui_map_obj['map']

        event_name = cast('str', event.get('name'))
        if ui_map is not None and event_name is not None and (event_name in ui_map):
            command = ui_map[event_name]
            if (command in self.command_map):
                self.command_map[command]()

        # Controller events are now handled via redux store subscriptions
        # in PerformFrame.check_state() and ControlDisplay.check_state()

    def get_parameters(self) -> list[AppParameter]:
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


    def __handle_store_update(self) -> None:
        self._dirty = True

    def _check_state(self) -> None:
        if not self._dirty:
            return
        self._dirty = False
        display_state = get_display_state()
        if (display_state['activeFrame'] != self.state.active_frame):
            if (display_state['activeFrame'] in self.frames):
                self.state.active_frame = display_state['activeFrame']
                self.frames[display_state['activeFrame']].tkraise()
            else:
                store.dispatch(actions.change_active_frame(self.state.active_frame))

    def toggle_menu(self) -> None:
        if (self.state.active_frame == "MENU"):
            self.state.active_frame = "PERFORM"
            self.frames["PERFORM"].tkraise()
        else:
            self.state.active_frame = "MENU"
            self.frames["MENU"].tkraise()

        store.dispatch(actions.change_active_frame(self.state.active_frame))


class DisplayState:
    active_frame: str = "PERFORM"
