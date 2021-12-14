def add(data):
  return {
    'type': 'controllerManager/controllerAdded',
    'payload': data
  }

def remove(data):
  return {
    'type': 'controllerManager/controllerRemoved',
    'payload': data
  } 

def updateMap(data):
  return {
    'type': 'controllerManager/controllerRemoved',
    'payload': data
  } 

def startWaitingForConnection():
  return {
    'type': 'controllerManager/startedWaitingForConnection'
  } 

def stopWaitingForConnection():
  return {
    'type': 'controllerManager/stoppedWaitingForConnection'
  }