from pyrsistent import freeze


def reducer(state, action):
  if state is None:
    return freeze({
      'waitingForConnection': False,
      'controllers': []
    })

  if action['type'] == 'controllerManager/controllerAdded':
    new_controller = freeze({
      'id': action['data']['id'],
      'name': action['data']['name'],
      'role': action['data']['role'],
      'compatibleMeMaps': action['data']['compatibleMeMaps'],
      'meMap': action['data']['meMap'],
      'uiMap': action['data']['uiMap']
    })
    new_controllers = state['controllers'].append(new_controller)
    return  state.set('controllers', new_controllers)

  if action['type'] == 'controllerManager/controllerRemoved':
    for controller in state['controllers']:
      if controller['id'] == action['data']['id']:
        new_controllers = state['controllers'].remove(controller)
        return state.set('controllers', new_controllers)
    return state

  if action['type'] == 'controllerManager/controllerMapUpdated':
    for index, controller in enumerate(state['controllers']):
      if controller['id'] == action['data']['id']:
        new_controller = controller.set('meMap', action['data']['meMap'])
        new_controllers =  state['controllers'].set(index, new_controller)
        return state.set('controllers', new_controllers)
    return state

  if action['type'] == 'controllerManager/startedWaitingForConnection':
    return state.set('waitingForConnection', True)

  if action['type'] == 'controllerManager/stoppedWaitingForConnection':
    return state.set('waitingForConnection', False)

  return state
