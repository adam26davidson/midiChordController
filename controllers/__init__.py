from .DualShock4 import DualShock
from .Wired360Controller import Wired360Controller
import asyncio
controllers = [DualShock, Wired360Controller]

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
      
