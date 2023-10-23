from typing import List, Dict
from controllerManager.controller import Controller
from controllerManager.models.mappableControl import MappableControl
from redux.reducers import controllerManager
from .controllers import controllerClasses
from redux import store
from redux.actions import controllerManager as actions
from redux.actions import controllerCoupler as ccActions
import asyncio

class ControllerManager():
  
    connectedControllers: List[Controller]

    def __init__(self):
        self.controllerClasses = controllerClasses
        self.connectedControllers = []
        self.subscriberCallbacks = []
        store.subscribe(self.handleStoreUpdate)
  
    def start(self):
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
        print("entering controller search loop")
        while (not foundController):
            print("checking for new connections")
            for controller in self.controllerClasses:
                foundController = controller.checkForNewConnections()
                if foundController:
                    print("found new controller")
                    connectedController: Controller = controller(self.sendEvent)
                    connectedController.open()
                    self.connectedControllers.append(connectedController)
                    store.dispatch(actions.stopWaitingForConnection())

                    controls = store.get_state()['controllerCoupler']['controls']
                    store.dispatch(ccActions.updateControls({**controls, **connectedController.getControls()}))
                    break
                else:
                    print("no new controller found")
            await asyncio.sleep(sleepTime)

    async def checkConnection(self):
        while True:
            self.connectedControllers = self.getUpdatedConnectedControllersList()
            if not self.connectedControllers:
                await self.waitForConnection()
            await asyncio.sleep(0.25)
  
    def getUpdatedConnectedControllersList(self):
        newConnectedControllerList = []
        for controller in self.connectedControllers:
            if controller.checkIfStillConnected():
                newConnectedControllerList.append(controller)
            else:
                controller.close()
        return newConnectedControllerList

    def handleStoreUpdate(self):
        pass