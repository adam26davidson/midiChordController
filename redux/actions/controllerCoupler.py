def updateControlMap(data):
  return {
    'type': 'controllerCoupler/controlMapUpdated',
    'data': data
  }

def updateAppParameters(data):
  return {
    'type': 'controllerCoupler/appParametersUpdated',
    'data': data
  }

def updateControls(data):
    return {
        'type': 'controllerCoupler/controlsUpdated',
        'data': data
    }

def musicEngineAppParametersLoaded():
    return {
        'type': 'controllerCoupler/musicEngineAppParametersLoaded'
    }