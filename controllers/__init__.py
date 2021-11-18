from .DualShock4 import DualShock
import asyncio
controllers = [DualShock]

async def searchForControllers():
  foundController = False
  connectedController = None
  while (not foundController):
    for Controller in controllers:
      foundController = Controller.checkIfConnected()
      if foundController:
        connectedController = Controller()
        connectedController.start()
        break
      asyncio.sleep(0.25)
      