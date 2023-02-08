from redux.reducers import controllerManager
from .controllers import controllerClasses
from redux import store
from redux.actions import controllerManager as actions
import asyncio

class ControllerManager():

  def __init__(self):
    self.controllerClasses = controllerClasses
    self.connectedControllers = []
    self.subscriberCallbacks = []
    store.subscribe(self.handleStoreUpdate)
  
  def start(self):
    # asyncio.ensure_future(self.waitForConnection())
    asyncio.ensure_future(self.checkConnection())

  def subscribe(self, callBack):
    self.subscriberCallbacks.append(callBack)

  def sendEvent(self, event):
    for callBack in self.subscriberCallbacks:
      callBack(event)

  async def waitForConnection(self, sleepTime=0.25):
    store.dispatch(actions.startWaitingForConnection())
    foundController = False
    connectedController = None
    while (not foundController):
      for controller in self.controllerClasses:
        foundController = controller.checkIfConnected()
        if foundController:
          connectedController = controller(self.sendEvent)
          connectedController.start()
          self.connectedControllers.append(connectedController)
          store.dispatch(actions.stopWaitingForConnection())
          break
        await asyncio.sleep(0.25)

  async def checkConnection(self):
    while True:
      self.connectedControllers = [c for c in self.connectedControllers if c.checkIfConnected()]
      if not self.connectedControllers:
        self.waitForConnection(0.02)

  def handleStoreUpdate(self):
    pass