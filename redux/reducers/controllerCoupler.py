from pyrsistent import freeze, thaw, m, pmap, v, pvector

def reducer(state, action):
    if state is None:
        return freeze({
            'activeControlMap': {},
            'appParameters': {},
            'controls': {}
        })

    if action['type'] == 'controllerCoupler/controlMapUpdated':
        return state.set('activeControlMap', action['data']['map'])
  
    elif action['type'] == 'controllerCoupler/appParametersUpdated':
        return state.set('appParameters', action['data'])
    
    elif action['type'] == 'controllerCoupler/controlsUpdated':
        return state.set('controls', action['data'])
    
    else: return state