def update_control_map(data):
  return {
    'type': 'controllerCoupler/controlMapUpdated',
    'data': data
  }

def update_app_parameters(data):
  return {
    'type': 'controllerCoupler/appParametersUpdated',
    'data': data
  }

def update_controls(data):
    return {
        'type': 'controllerCoupler/controlsUpdated',
        'data': data
    }

def music_engine_app_parameters_loaded():
    return {
        'type': 'controllerCoupler/musicEngineAppParametersLoaded'
    }
