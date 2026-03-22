from __future__ import annotations

from typing import Any

from redux.types import ReduxAction


def add(data: Any) -> ReduxAction:
  return {
    'type': 'controllerManager/controllerAdded',
    'data': data
  }

def remove(data: Any) -> ReduxAction:
  return {
    'type': 'controllerManager/controllerRemoved',
    'data': data
  }

def update_map(data: Any) -> ReduxAction:
  return {
    'type': 'controllerManager/controllerMapUpdated',
    'data': data
  }

def start_waiting_for_connection() -> ReduxAction:
  return {
    'type': 'controllerManager/startedWaitingForConnection'
  }

def stop_waiting_for_connection() -> ReduxAction:
  return {
    'type': 'controllerManager/stoppedWaitingForConnection'
  }
