from pyrsistent import freeze, thaw, m, pmap, v, pvector
def controllerReducer(state, action):
  if state is None:
    state = m()

  if action['type'] == 'ADD_CONTROLLER':
    controllers = state['controllers']
    newController = freeze({
      'id': action['payload']['id'],
      'role': action['payload']['role'],
      'compatibleMeMaps': action['payload']['compatibleMeMaps'],
      'meMap': action['payload']['meMap'],
      'uiMap': action['payload']['uiMap']
    })
    newControllers = controllers.append(newController)
    return state.set('controllers', newControllers)

  elif action['type'] == 'REMOVE_CONTROLLER':
    controllers = state['controllers']
    for controller in controllers:
      if controller['id'] == action['payload']['id']:
        newControllers = controllers.remove(controller)
        return state.set('controllers', newControllers)
    return state
    
  elif action['type'] == 'UPDATE_CONTROLLER_MAP':
    for index, controller in enumerate(state['controllers']):
      if controller['id'] == action['payload']['id']:
        newController = controller.set('meMap', action['payload']['meMap'])
        newControllers = state['controllers'].set(index, newController)
        return state.set('controllers', newControllers)
    return state