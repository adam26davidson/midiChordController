import evdev
import asyncio
import math
import time
from constants import *
from midiController import MidiController
from .config import config

class Wired360Controller(MidiController):
    def __init__(self, display):
        super().__init__(display)
        self.config = config
        self.leftTriggerDown = False
        self.rightTriggerDown = False
        self.absValues = {
            "gyroX": {"processed": 0, "past": []},
            "leftJoyY": {"processed": 0, "past": []},
            "rightJoyY": {"processed": 0, "past": []}
        }
        self.lastMidiUpdate = time.time()

    def start(self):
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for device in devices:
            if device.name == "Microsoft X-Box 360 pad":
                self.buttons = evdev.InputDevice(device.path)
                asyncio.ensure_future(self.buttonsLoop())
            if self.display: self.display.setController(self.config["name"])
        super().start()

    def checkIfConnected():
        found = False
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for device in devices:
            if (device.name == "Microsoft X-Box 360 pad"):
                found = True

        return found

    async def buttonsLoop(self):
        async for event in self.buttons.async_read_loop():
            forceUpdate = True
            if event.type == evdev.ecodes.EV_KEY:
                for button in ["south", "east", "north", "west"]:
                    if event.code == self.config["buttonCodes"][button]:
                        if event.value == 1:
                            self.playChord(button)
                        elif self.activeChord == button:
                            self.stopChord()

                if event.code == self.config["buttonCodes"]["leftTrigger"]:
                    if event.value == 1:
                        self.leftTriggerDown = True
                        self.setModulation("left")
                    else:
                        self.leftTriggerDown = False
                        if self.rightTriggerDown:
                            self.setModulation("right")
                        else:
                            self.setModulation("none")

                elif event.code == self.config["buttonCodes"]["rightTrigger"]:
                    if event.value == 1:
                        self.rightTriggerDown = True
                        self.setModulation("right")
                    else:
                        self.rightTriggerDown = False
                    if self.leftTriggerDown:
                        self.setModulation("left")
                    else:
                        self.setModulation("none")

                elif event.code == self.config["buttonCodes"]["options"]:
                    if event.value == 1:
                        self.toggleShift()
                elif event.code == self.config["buttonCodes"]["share"]:
                    if event.value == 1:
                        self.toggleAlt()

            elif event.type == evdev.ecodes.EV_ABS:
                if event.code == self.config["buttonCodes"]["leftTrigger2"]:
                    if event.value > 1:
                        self.playBass()
                    else:
                        self.stopBass()
                if event.code == self.config["buttonCodes"]["rightTrigger2"]:
                    if event.value > 1:
                        self.setAlternate(True)
                    else:
                        self.setAlternate(False)

                if event.code == self.config["absCodes"]["leftJoyY"]:
                    intValue, value = self.processInversionValue(
                        event.value, 
                        "leftJoyY", 
                        self.config, 
                        self.absValues["leftJoyY"], 
                        type="bass")
                    self.setBassPosition(intValue, value)
                    forceUpdate = False
                
                if event.code == self.config["absCodes"]["rightJoyY"]:
                    if (not self.inversionHold):
                        intValue, value = self.processInversionValue(
                            event.value,
                            "rightJoyY",
                            self.config,
                            self.absValues["rightJoyY"]
                        )
                        self.setInversion(intValue, value)
                if event.code == self.config["absCodes"]["padX"]:
                    if event.value == -1:
                        self.setSecondary("left")
                    elif event.value == 0:
                        self.setSecondary("none")
                    elif event.value == 1:
                        self.setSecondary("right")

                elif event.code == self.config["absCodes"]["padY"]:
                    if not self.shift and not self.alt:
                        if event.value == -1:
                            self.incrementSpread()
                        elif event.value == 1:
                            self.decrementSpread()
                    elif self.shift and not self.alt:
                        if event.value == -1:
                            self.incrementKey()
                        elif event.value == 1:
                            self.decrementKey()
                    elif not self.shift and self.alt:
                        if event.value == -1:
                            self.incrementSetting()
                        elif event.value == 1:
                            self.decrementSetting()
                    else:
                        if event.value == -1:
                            self.toggleHold()
                        if event.value == 1:
                            self.toggleInversionHold()
        if (forceUpdate):
            self.updateDisplay()
