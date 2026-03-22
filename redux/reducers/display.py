from __future__ import annotations

from typing import TYPE_CHECKING

from pyrsistent import freeze

from redux.types import ReduxAction

if TYPE_CHECKING:
    from pyrsistent.typing import PMap


def reducer(state: PMap[str, object] | None, action: ReduxAction) -> PMap[str, object]:
    if state is None:
        return freeze({
            'activeFrame': 'PERFORM'
        })

    if action['type'] == 'ui/activeFrameChanged':
        return state.set('activeFrame', action['data']['activeFrame'])
    return state
