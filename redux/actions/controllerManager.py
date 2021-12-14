def add(data):
  return {
    'type': 'controllerManager/controllerAdded',
    'data': data
  }

def remove(data):
  return {
    'type': 'controllerManager/controllerRemoved',
    'data': data
  } 

def updateMap(data):
  return {
    'type': 'controllerManager/controllerRemoved',
    'data': data
  } 

def startWaitingForConnection():
  return {
    'type': 'controllerManager/startedWaitingForConnection'
  } 

def stopWaitingForConnection():
  return {
    'type': 'controllerManager/stoppedWaitingForConnection'
  }