from pyrsistent import freeze


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

    if action['type'] == 'controllerCoupler/appParametersUpdated':
        return state.set('appParameters', action['data'])

    if action['type'] == 'controllerCoupler/controlsUpdated':
        return state.set('controls', action['data'])

    if action['type'] == 'controllerCoupler/musicEngineAppParametersLoaded':
        return state.set('musicEngineAppParametersLoaded', True)

    return state
