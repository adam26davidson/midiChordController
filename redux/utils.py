from . import store

def getActiveMeMap():
    return getActiveMap('meMap')

def getActiveUiMap():
    return getActiveMap('uiMap')

def getActiveMap(mapType):
    map = None

    controllers = store.get_state()['controllerManager']['controllers']
    for controller in controllers:
        if controller['role'] == 'primary':
            map = controller[mapType]['map']
            break

    return map