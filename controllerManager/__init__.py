from .controllers import controllerClasses
import asyncio

class controllerManager():
  def __init__(self):
    self.controllerClasses = controllerClasses
    self.connectedControllers = {}
    self.subscriberCallbacks = []

  def subscribe(self, callBack):
    self.subscriberCallbacks.append(callBack)

  def sendEvent(self, event):
    for callBack in self.subscriberCallbacks:
      callBack(event)

  async def searchForControllers(display):
    foundController = False
    connectedController = None
    while (not foundController):
      for Controller in controllers:
        foundController = Controller.checkIfConnected()
        if foundController:
          connectedController = Controller(display)
          connectedController.start()
          break
        await asyncio.sleep(0.25)
      
