from __future__ import annotations

import asyncio
import logging
from typing import Callable

from controller_manager.controller import Controller
from controller_manager.models.control_event import ControlEvent
from controller_manager.models.mappable_control import MappableControl  # noqa: F401
from redux import get_controller_coupler_state, store
from redux.actions import controller_coupler as cc_actions
from redux.actions import controller_manager as actions
from redux.reducers import controller_manager  # noqa: F401

from .controllers import controller_classes

logger = logging.getLogger(__name__)


class ControllerManager:

    connected_controllers: list[Controller]

    def __init__(self) -> None:
        self.controller_classes = controller_classes
        self.connected_controllers = []
        self.subscriber_callbacks: list[Callable[[ControlEvent], None]] = []
        store.subscribe(self.handle_store_update)

    def start(self) -> None:
        _task = asyncio.ensure_future(self.check_connection())

    def subscribe(self, callback: Callable[[ControlEvent], None]) -> None:
        self.subscriber_callbacks.append(callback)

    def send_event(self, event: ControlEvent) -> None:
        for callback in self.subscriber_callbacks:
            callback(event)

    async def wait_for_connection(self, sleep_time: float = 0.25) -> None:
        loop = asyncio.get_event_loop()
        store.dispatch(actions.start_waiting_for_connection())
        found_controller = False
        connected_controller = None
        logger.info("entering controller search loop")
        while (not found_controller):
            logger.debug("checking for new connections")
            for controller in self.controller_classes:
                found_controller = await loop.run_in_executor(
                    None, controller.check_for_new_connections)
                if found_controller:
                    logger.info("found new controller")
                    connected_controller: Controller = controller(self.send_event)
                    connected_controller.open()
                    self.connected_controllers.append(connected_controller)
                    store.dispatch(actions.stop_waiting_for_connection())

                    controls = get_controller_coupler_state()['controls']
                    store.dispatch(cc_actions.update_controls({**controls, **connected_controller.get_controls()}))
                    break
                logger.debug("no new controller found")
                await asyncio.sleep(sleep_time)

    async def check_connection(self) -> None:
        loop = asyncio.get_event_loop()
        while True:
            self.connected_controllers = await loop.run_in_executor(
                None, self._get_updated_connected_controllers_list)
            if not self.connected_controllers:
                await self.wait_for_connection()
            await asyncio.sleep(0.25)

    def _get_updated_connected_controllers_list(self) -> list[Controller]:
        new_connected_controller_list: list[Controller] = []
        for controller in self.connected_controllers:
            if controller.check_if_still_connected():
                new_connected_controller_list.append(controller)
            else:
                controller.close()
        return new_connected_controller_list

    def handle_store_update(self) -> None:
        pass
