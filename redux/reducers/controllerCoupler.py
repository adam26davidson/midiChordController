from pyrsistent import freeze, thaw, m, pmap, v, pvector

def reducer(state, action):
    if state is None:
        return freeze({
            'activeControlMap': None,
            'appParameters': {},
            'controls': {},
            'musicEngineAppParametersLoaded': False,
        })

    if action['type'] == 'controllerCoupler/controlMapUpdated':
        return state.set('activeControlMap', action['data'])
  
    elif action['type'] == 'controllerCoupler/appParametersUpdated':
        return state.set('appParameters', action['data'])
    
    elif action['type'] == 'controllerCoupler/controlsUpdated':
        return state.set('controls', action['data'])

    elif action['type'] == 'controllerCoupler/musicEngineAppParametersLoaded':
        return state.set('musicEngineAppParametersLoaded', True)
    
    else: return state