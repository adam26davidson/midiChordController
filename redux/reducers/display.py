from pyrsistent import freeze


def reducer(state, action):
    if state is None:
        return freeze({
            'activeFrame': 'PERFORM' 
        })
    
    if action['type'] == 'ui/activeFrameChanged':
        return state.set('activeFrame', action['data']['activeFrame'])
    else:
        return state