from .DualShock4 import DualShock
import asyncio
controllers = [DualShock]

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
      