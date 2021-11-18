import evdev
import asyncio
import math
import time
from constants import * 
from midiController import MidiController
from .config import config

class DualShock(MidiController):
  def __init__(self):
    super().__init__()
    self.config = config
    self.leftTriggerDown = False
    self.rightTriggerDown = False
    self.absValues = {
      "gyroX": {"processed": 0, "past": []},
      "leftJoyY": {"processed": 0, "past": []}
    }
    self.lastMidiUpdate = time.time()
    self.lastUpdate = time.time()
    self.controllerFound = False

  def start(self):
    super().start()
    asyncio.ensure_future(self.findController())

  def __processValue(self, rawValue, name, maxSteps):
    range = self.config["ranges"][name]
    pastValues = self.absValues[name]["raw"]

    pastValues.append(rawValue)
    if (len(pastValues) > self.config["absAverageCounts"][name]):
      pastValues.pop(0)

    # get the average of the past raw values (prevents jitter)
    sum = 0
    for val in pastValues:
      sum += val
    avg = sum / len(pastValues)

    #clamp value to between -0.999 and 0.999
    slope = 2.0 / (range["top"]- range["bottom"])
    intercept = 1 - (slope*range["top"])
    normalized =  (slope*avg) + intercept
    normalized = max(min(normalized, 0.999), -0.999)
    
    #
    def getValue(n):
      if n > 0:
        return math.floor(n * (maxSteps + 1))
      else:
        return math.ceil(n * (maxSteps + 1))

    # snap processed value back into current window if     
    snapped = normalized
    value = getValue(snapped)
    snap = (1.0 / (maxSteps + 1)) * INVERSION_SNAP

    if value == self.absValues[name]["processed"] + 1:
      snapped -= snap
      value = getValue(snapped)
    if value == self.absValues[name]["processed"] - 1:
      snapped += snap
      value = getValue(snapped)
    
    self.absValues[name]["processed"] = value
    return value, normalized

  async def findController(self):
    while (not self.controllerFound):
      self.controllerFound = False
      devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
      print(device.name for device in devices)
      for device in devices:
        if (device.name == "Wireless Controller"):
          self.buttons = evdev.InputDevice(device.path)
          self.controllerFound = True
          print("FOUND CONTROLLER")
        elif (device.name == "Wireless Controller Motion Sensors"):
          self.motion = evdev.InputDevice(device.path)
        elif (device.name == "Wireless Controller Touchpad"):
          self.touch = evdev.InputDevice(device.path)

      if (self.controllerFound):
        asyncio.ensure_future(self.motionLoop())
        asyncio.ensure_future(self.buttonsLoop())
        asyncio.ensure_future(self.touchLoop())
        self.display.setController("DualShock4")
      
      await asyncio.sleep(0.5)

  async def motionLoop(self):
    async for event in self.motion.async_read_loop():
      if event.code == self.config["motionCodes"]["x"]:
        if (not self.inversionHold):
          intValue, value = self.__processValue(event.value, "gyroX", self.inversionRange)
          self.setInversion(intValue, value)
      elif event.code == self.config["motionCodes"]["z"]:
        t = time.time()
        if event.value != 0 and (t - self.lastMidiUpdate) > MIDI_STEP:
          max = self.config["ranges"]["gyroZ"]["bottom"]
          value = math.floor((min(abs(event.value), max) / max)*127)
          self.setAfterTouch(value)
          self.lastMidiUpdate = t
  
  async def buttonsLoop(self):
    async for event in self.buttons.async_read_loop():
      forceUpdate = True
      if event.type == evdev.ecodes.EV_KEY:
        for button in ["south", "east", "north", "west"]:
          if event.code == self.config["buttonCodes"][button]:
            if event.value == 1:
              self.playChord(button)
            elif self.activeChord == button and not self.hold:
              self.stopChord()
        if event.code == self.config["buttonCodes"]["leftTrigger2"]:
          if event.value == 1:
            self.playBass()
          elif not self.hold:
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
          intValue, value = self.__processValue(event.value, "leftJoyY", self.bassRange)
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
