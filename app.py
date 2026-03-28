from __future__ import annotations

import asyncio
import atexit
import logging
import os
import signal
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from controller_coupler import ControllerCoupler
from controller_manager import ControllerManager
from display import Display
from music_engine import MusicEngine
from redux.settings_storage import settings_storage_utility
from remote_control import RemoteControlServer

if TYPE_CHECKING:
    import argparse

logger = logging.getLogger(__name__)

LOCK_FILE = Path("/tmp/midichordcontroller.lock")


def _remove_lock() -> None:
    LOCK_FILE.unlink(missing_ok=True)


def _acquire_app_lock() -> None:
    if LOCK_FILE.exists():
        try:
            existing_pid = int(LOCK_FILE.read_text().strip())
            os.kill(existing_pid, 0)  # Check if process is alive
            logger.error("Another instance is already running (PID %d).", existing_pid)
            sys.exit(1)
        except (ValueError, ProcessLookupError, PermissionError):
            # Stale lock — process is gone
            LOCK_FILE.unlink(missing_ok=True)

    LOCK_FILE.write_text(str(os.getpid()))
    atexit.register(_remove_lock)
    signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(0))


class App:

    controller_manager: ControllerManager
    controller_coupler: ControllerCoupler
    music_engine: MusicEngine
    display: Display
    remote_control_server: RemoteControlServer | None

    def __init__(self, args: argparse.Namespace) -> None:
        _acquire_app_lock()
        self.use_display: bool = args.display
        if (self.use_display):
            self.display = Display()
        self.controller_manager = ControllerManager()
        self.controller_coupler = ControllerCoupler()
        self.music_engine = MusicEngine()

        self.controller_manager.subscribe(self.controller_coupler.event_handler)

        if args.remote_control:
            self.remote_control_server = RemoteControlServer(
                self.controller_coupler.event_handler,
                midi_history=self.music_engine.midi.history,
                midi=self.music_engine.midi,
            )
        else:
            self.remote_control_server = None


    def start(self) -> None:
        settings_storage_utility.load_settings()

        if (self.use_display):
            self.display.start()
        self.music_engine.start()
        self.controller_manager.start()
        if self.remote_control_server:
            self.remote_control_server.start()

        asyncio.get_event_loop().run_forever()
