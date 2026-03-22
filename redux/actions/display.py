from __future__ import annotations

from redux.types import ReduxAction


def change_active_frame(frame: str) -> ReduxAction:
  return{
    'type': 'ui/activeFrameChanged',
    'data': {'activeFrame': frame}
  }
