from __future__ import annotations

from typing import cast

import pydux
from pyrsistent import thaw

from .reducers import controller_coupler, controller_manager, display, music_engine
from .types import (
    ControllerCouplerState,
    ControllerManagerState,
    DisplayState,
    MusicEngineState,
)

reducer = pydux.combine_reducers({
    'controllerManager': controller_manager.reducer,
    'controllerCoupler': controller_coupler.reducer,
    'musicEngine': music_engine.reducer,
    'display': display.reducer
})

store = pydux.create_store(reducer)


def get_music_engine_state() -> MusicEngineState:
    return cast('MusicEngineState', thaw(store.get_state()['musicEngine']))


def get_controller_manager_state() -> ControllerManagerState:
    return cast('ControllerManagerState', thaw(store.get_state()['controllerManager']))


def get_controller_coupler_state() -> ControllerCouplerState:
    return cast('ControllerCouplerState', thaw(store.get_state()['controllerCoupler']))


def get_display_state() -> DisplayState:
    return cast('DisplayState', thaw(store.get_state()['display']))
