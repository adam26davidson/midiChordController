import evdev
import asyncio
import math
import time
from constants import * 
from midiController import MidiController
from .config import config

class DualShock4(MidiController):
  config = config
  library = None

  def __init__(self, display):
    super().__init__(display)
    self.leftTriggerDown = False
    self.rightTriggerDown = False
    self.absValues = {
      "gyroX": {"processed": 0, "past": []},
      "leftJoyY": {"processed": 0, "past": []}
    }

  def start(self):
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
      if (device.name == "Wireless Controller"):
        self.buttons = evdev.InputDevice(device.path)
        asyncio.ensure_future(self.buttonsLoop())
      elif (device.name == "Wireless Controller Motion Sensors"):
        self.motion = evdev.InputDevice(device.path)
        asyncio.ensure_future(self.motionLoop())
      elif (device.name == "Wireless Controller Touchpad"):
        self.touch = evdev.InputDevice(device.path)
        asyncio.ensure_future(self.touchLoop())

      self.display.setController(self.config["name"])
    super().start()

  def checkIfConnected():
      found = False
      devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
      for device in devices:
        if (device.name == "Wireless Controller"):
          found = True
        elif (device.name == "Wireless Controller Motion Sensors"):
          found = True
        elif (device.name == "Wireless Controller Touchpad"):
          found = True
      return found

  async def motionLoop(self):
    async for event in self.motion.async_read_loop():
      if event.code == self.config["motionCodes"]["x"]:
        if (not self.inversionHold):
          intValue, value = self.processInversionValue(event.value, "gyroX", self.config, self.absValues["gyroX"])
          self.setInversion(intValue, value)
      elif event.code == self.config["motionCodes"]["z"]:
        if event.value != 0:
          value = self.processCCValue(event.value, "gyroZ", self.config)
          self.setAfterTouch(value)
  
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
        if event.code == self.config["buttonCodes"]["leftTrigger2"]:
          if event.value == 1:
            self.playBass()
          else:
            self.stopBass()
        elif event.code == self.config["buttonCodes"]["rightTrigger2"]:
          if event.value == 1:
            self.setAlternate(True)
          else:
            self.setAlternate(False)
        elif event.code == self.config["buttonCodes"]["leftTrigger"]:
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
        if event.code == self.config["absCodes"]["leftJoyY"]:
          intValue, value = self.processInversionValue(
            event.value, 
            "leftJoyY", 
            self.config, 
            self.absValues["leftJoyY"], 
            type="bass")
          self.setBassPosition(intValue, value)
          forceUpdate = False
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

  async def touchLoop(self):
    async for event in self.touch.async_read_loop():
      pass
