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

def update_map(data):
  return {
    'type': 'controllerManager/controllerMapUpdated',
    'data': data
  }

def start_waiting_for_connection():
  return {
    'type': 'controllerManager/startedWaitingForConnection'
  }

def stop_waiting_for_connection():
  return {
    'type': 'controllerManager/stoppedWaitingForConnection'
  }
