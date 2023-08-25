from . import store

def getActiveMeMap():
    meMap = None

    controllers = store.get_state()['controllerManager']['controllers']
    for controller in controllers:
        if controller['role'] == 'primary':
            meMap = controller['meMap']['map']
            break

    return meMap