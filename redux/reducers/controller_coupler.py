from __future__ import annotations

from typing import TYPE_CHECKING

from pyrsistent import freeze

from redux.types import ReduxAction

if TYPE_CHECKING:
    from pyrsistent.typing import PMap


def reducer(state: PMap[str, object] | None, action: ReduxAction) -> PMap[str, object]:
    if state is None:
        return freeze({
            'activeControlMap': None,
            'appParameters': {},
            'controls': {},
            'musicEngineAppParametersLoaded': False,
        })

    if action['type'] == 'controllerCoupler/controlMapUpdated':
        return state.set('activeControlMap', action['data'])

    if action['type'] == 'controllerCoupler/appParametersUpdated':
        return state.set('appParameters', action['data'])

    if action['type'] == 'controllerCoupler/controlsUpdated':
        return state.set('controls', action['data'])

    if action['type'] == 'controllerCoupler/musicEngineAppParametersLoaded':
        return state.set('musicEngineAppParametersLoaded', True)

    return state
