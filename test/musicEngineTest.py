from controllerManager import ControllerManager
from musicEngine import MusicEngine
from redux import store

def musicEngineTest():
  c = ControllerManager()
  m = MusicEngine()


  def handleControllerEvent(event):
    if 'value' not in event.keys():
      print(event['name'])

  def handleStateChange():
      print('STATE UPDATE')
      controllers = store.get_state()['controllerManager']['controllers']
      waiting = store.get_state()['controllerManager']['waitingForConnection']
      print([c['name'] for c in controllers])
      print('waitingForConnection: ' + str(waiting))

  c.subscribe(m.controllerEventHandler)
  c.subscribe(handleControllerEvent)
  store.subscribe(handleStateChange)

  m.start()
  c.start()