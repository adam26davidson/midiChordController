from controller_manager import ControllerManager
from redux import store


def controller_manager_test():
  c = ControllerManager()

  def handle_controller_event(event):
    if 'value' not in event:
      print(event['name'])

  def handle_state_change():
      print('STATE UPDATE')
      controllers = store.get_state()['controllerManager']['controllers']
      waiting = store.get_state()['controllerManager']['waitingForConnection']
      print([c['name'] for c in controllers])
      print('waitingForConnection: ' + str(waiting))

  c.subscribe(handle_controller_event)
  store.subscribe(handle_state_change)

  c.start()
