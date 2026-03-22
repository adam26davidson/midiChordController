from __future__ import annotations

from typing import TYPE_CHECKING, cast

from pyrsistent import freeze

from redux.types import ReduxAction

if TYPE_CHECKING:
  from pyrsistent.typing import PMap, PVector


def reducer(state: PMap[str, object] | None, action: ReduxAction) -> PMap[str, object]:
  if state is None:
    return freeze({
      'waitingForConnection': False,
      'controllers': []
    })

  controllers = cast('PVector[PMap[str, object]]', state['controllers'])

  if action['type'] == 'controllerManager/controllerAdded':
    new_controller = freeze({
      'id': action['data']['id'],
      'name': action['data']['name'],
      'role': action['data']['role'],
      'compatibleMeMaps': action['data']['compatibleMeMaps'],
      'meMap': action['data']['meMap'],
      'uiMap': action['data']['uiMap']
    })
    new_controllers = controllers.append(new_controller)
    return state.set('controllers', new_controllers)

  if action['type'] == 'controllerManager/controllerRemoved':
    for controller in controllers:
      if controller['id'] == action['data']['id']:
        new_controllers = controllers.remove(controller)
        return state.set('controllers', new_controllers)
    return state

  if action['type'] == 'controllerManager/controllerMapUpdated':
    for index, controller in enumerate(controllers):
      if controller['id'] == action['data']['id']:
        new_controller = controller.set('meMap', action['data']['meMap'])
        new_controllers = controllers.set(index, new_controller)
        return state.set('controllers', new_controllers)
    return state

  if action['type'] == 'controllerManager/startedWaitingForConnection':
    return state.set('waitingForConnection', True)

  if action['type'] == 'controllerManager/stoppedWaitingForConnection':
    return state.set('waitingForConnection', False)

  return state
