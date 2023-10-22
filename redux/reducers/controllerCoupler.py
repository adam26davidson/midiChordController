from pyrsistent import freeze, thaw, m, pmap, v, pvector

def reducer(state, action):
    if state is None:
        return freeze({
            'activeControlMap': {},
            'appParameters': None
        })

    if action['type'] == 'controllerCoupler/controlMapUpdated':
        return state.set('activeControlMap', action['data']['map'])
  
    elif action['type'] == 'controllerCoupler/appParametersUpdated':
        return state.set('appParameters', action['data'])
    
    else: return state