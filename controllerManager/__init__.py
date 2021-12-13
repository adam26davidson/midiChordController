from .controllers import controllerClasses
from .functionMaps import meMap, uiMaps
import asyncio

class controllerManager():
  def __init__(self):
    self.controllerClasses = controllerClasses
    self.connectedControllers = {}
    self.subscriberCallbacks = []

  def subscribe(self, callBack):
    self.subscriberCallbacks.append(callBack)

  async def sendEvent(self, event):
    for callBack in self.subscriberCallbacks:
      callBack(event)

  async def searchForControllers(self):
    foundController = False
    connectedController = None
    while (not foundController):
      for Controller in controllers:
        foundController = Controller.checkIfConnected()
        if foundController:
          connectedController = Controller(self.sendEvent)
          connectedController.start()
          break
        await asyncio.sleep(0.25)
      
