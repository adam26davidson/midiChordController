from redux.reducers import controllerManager
from .controllers import controllerClasses
from redux import store
from redux.actions import controllerManager as actions
import asyncio

class ControllerManager():

  def __init__(self):
    self.controllerClasses = controllerClasses
    self.connectedControllers = {}
    self.subscriberCallbacks = []
    store.subscribe(self.handleStoreUpdate)

  def subscribe(self, callBack):
    self.subscriberCallbacks.append(callBack)

  async def sendEvent(self, event):
    for callBack in self.subscriberCallbacks:
      callBack(event)

  async def waitForConnection(self):
    store.dispatch(actions.startWaitingForConnection())
    foundController = False
    connectedController = None
    while (not foundController):
      for Controller in controllerClasses:
        foundController = Controller.checkIfConnected()
        if foundController:
          connectedController = Controller(self.sendEvent)
          connectedController.start()
          self.connectedControllers = [connectedController]
          store.dispatch(actions.stopWaitingForConnection())
          break
        await asyncio.sleep(0.25)
      
  async def handleStoreUpdate():
    print('STATE UPDATE')
    controllers = store.get_state()['controllerManager']['controllers']
    print([c['name'] for c in controllers])