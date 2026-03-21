
from models.appParameter import AppParameter

from . import store
from .actions import controllerCoupler as ccActions


def get_active_me_map():
    return get_active_map('meMap')

def get_active_ui_map():
    return get_active_map('uiMap')

def get_active_map(map_type):
    map = None

    controllers = store.get_state()['controllerManager']['controllers']
    for controller in controllers:
        if controller['role'] == 'primary':
            map = controller[map_type]['map']
            break

    return map

def add_app_parameters(parameters: list[AppParameter]):
    print(f"adding {len(parameters)} parameters")
    state = store.get_state()['controllerCoupler']
    existing_params = state['appParameters']
    new_params = {param.key: param for param in parameters}
    if existing_params:
        store.dispatch(ccActions.update_app_parameters({**existing_params, **new_params}))
    else:
        store.dispatch(ccActions.update_app_parameters(new_params))
    new_state = store.get_state()['controllerCoupler']
    print(f"new parameterCount: {len(new_state['appParameters'])}")
