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