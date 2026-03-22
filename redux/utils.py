from __future__ import annotations

from typing import Any

from models.app_parameter import AppParameter

from . import get_controller_coupler_state, get_controller_manager_state, store
from .actions import controller_coupler as cc_actions


def get_active_me_map() -> Any | None:
    controllers = get_controller_manager_state()['controllers']
    for controller in controllers:
        if controller['role'] == 'primary':
            me_map = controller['meMap']
            if me_map is not None:
                return me_map['map']
    return None

def get_active_ui_map() -> Any | None:
    controllers = get_controller_manager_state()['controllers']
    for controller in controllers:
        if controller['role'] == 'primary':
            ui_map = controller['uiMap']
            if ui_map is not None:
                return ui_map['map']
    return None

def add_app_parameters(parameters: list[AppParameter]) -> None:
    print(f"adding {len(parameters)} parameters")
    state = get_controller_coupler_state()
    existing_params = state['appParameters']
    new_params = {param.key: param for param in parameters}
    if existing_params:
        store.dispatch(cc_actions.update_app_parameters({**existing_params, **new_params}))
    else:
        store.dispatch(cc_actions.update_app_parameters(new_params))
    new_state = get_controller_coupler_state()
    print(f"new parameterCount: {len(new_state['appParameters'])}")
