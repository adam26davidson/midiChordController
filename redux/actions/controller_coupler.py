from __future__ import annotations

from typing import Any

from redux.types import ReduxAction


def update_control_map(data: Any) -> ReduxAction:
  return {
    'type': 'controllerCoupler/controlMapUpdated',
    'data': data
  }

def update_app_parameters(data: Any) -> ReduxAction:
  return {
    'type': 'controllerCoupler/appParametersUpdated',
    'data': data
  }

def update_controls(data: Any) -> ReduxAction:
    return {
        'type': 'controllerCoupler/controlsUpdated',
        'data': data
    }

def music_engine_app_parameters_loaded() -> ReduxAction:
    return {
        'type': 'controllerCoupler/musicEngineAppParametersLoaded'
    }
