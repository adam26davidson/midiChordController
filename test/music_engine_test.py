from controller_manager import ControllerManager
from display import Display
from music_engine import MusicEngine


def music_engine_test():
  d = Display()
  c = ControllerManager()
  m = MusicEngine()

  # def handle_controller_event(event):
  #   if 'value' not in event.keys():
  #     print(event['name'])
  #   if event['name'] == 'RIGHT_STICK_Y_UPDATE':
  #     print(event)

  # def handle_state_change():
  #   controllers = store.get_state()['controllerManager']['controllers']
  #   waiting = store.get_state()['controllerManager']['waitingForConnection']

  c.subscribe(m.controllerEventHandler)
  c.subscribe(d.controller_event_handler)
  #c.subscribe(handle_controller_event)
  # store.subscribe(handle_state_change)

  d.start()
  m.start()
  c.start()
