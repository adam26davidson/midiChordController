from pyrsistent import freeze, thaw, m, pmap, v, pvector

def reducer(state, action):
  if state is None:
    state = freeze({
      'waitingForConnection': False,
      'controllers': []
    })

  if action['type'] == 'controllerManager/controllerAdded':
    newController = freeze({
      'id': action['data']['id'],
      'role': action['data']['role'],
      'compatibleMeMaps': action['data']['compatibleMeMaps'],
      'meMap': action['data']['meMap'],
      'uiMap': action['data']['uiMap']
    })
    newControllers = state['controllers'].append(newController)
    return  state.set('controllers', newControllers)

  elif action['type'] == 'controllerManager/controllerRemoved':
    for controller in state['controllers']:
      if controller['id'] == action['data']['id']:
        newControllers = state['controllers'].remove(controller)
        return state.set('controllers', newControllers)
    return state

  elif action['type'] == 'controllerManager/controllerMapUpdated':
    for index, controller in enumerate(state['controllers']):
      if controller['id'] == action['data']['id']:
        newController = controller.set('meMap', action['data']['meMap'])
        newControllers =  state['controllers'].set(index, newController)
        return state.set('controllers', newControllers)
    return state

  elif action['type'] == 'controllerManager/startedWaitingForConnection':
    return state.set('waitingForConnection', True)

  elif action['type'] == 'controllerManager/stoppedWaitingForConnection':
    return state.set('waitingForConnection', False)