from typing import List

from models.appParameter import AppParameter
from . import store
from .actions import controllerCoupler as ccActions

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

def addAppParameters(parameters: List[AppParameter]):
    state = store.get_state()['controllerCoupler']
    existingParams = state['appParameters']
    newParams = {param.key: param for param in parameters}
    if existingParams:
        store.dispatch(ccActions.updateAppParameters({**existingParams, **newParams}))
    else:
        store.dispatch(ccActions.updateAppParameters(newParams))