from controllerManager import ControllerManager
from musicEngine import MusicEngine
from redux import store

def musicEngineTest():
  c = ControllerManager()
  m = MusicEngine()


  def handleControllerEvent(event):
    if 'value' not in event.keys():
      print(event['name'])

  # def handleStateChange():
  #   controllers = store.get_state()['controllerManager']['controllers']
  #   waiting = store.get_state()['controllerManager']['waitingForConnection']

  c.subscribe(m.controllerEventHandler)
  c.subscribe(handleControllerEvent)
  # store.subscribe(handleStateChange)

  m.start()
  c.start()