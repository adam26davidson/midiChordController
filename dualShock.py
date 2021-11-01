import evdev
import asyncio
import math
import time
from constants import *

class DualShock:
  def __init__(self, midiShock):
    self.midiShock = midiShock
    print(evdev.list_devices())
    self.state = {
      "lt": False,
      "rt": False,
      "gyroX": 0,
      "lJoyY": 127
    }
    self.pastValues = {
      "gyroX": {"n": 4, "values": []},
      "lJoyY": {"n": 1, "values": []}
      }
    self.gyroSnap = INVERSION_SNAP
    self.gyroThumbValue = 0
    self.lJoyYThumbValue = 127
    self.buttonCodes = {"ex": 304, "square": 308, "triangle": 307, "circle": 305, "rt": 311, "rt2": 313, "lt": 310, "lt2": 312, "options": 315, "share": 314}
    self.absCodes = {"padX": 16, "padY": 17, "lJoyX": 0, "lJoyY": 1, "rJoyX": 3, "rJoyY": 4}
    self.motionCodes = {"x": 2, "z": 0}
    self.ranges = {
      "gyroX": {"top": -8050, "bottom": 8050},
      "gyroZ": {"top": -8050, "bottom": 8050},
      "lJoyY": {"top": 0, "bottom": 255},
    }
    self.midiMessageRate = 1 / 30
    self.lastMidiUpdate = time.time()
    self.lastUpdate = time.time()
    self.controllerFound = False

    asyncio.ensure_future(self.findController())

  def processValue(self, rawValue, name, maxSteps):
    range = self.ranges[name]
    pastValues = self.pastValues[name]["values"]

    pastValues.append(rawValue)
    if (len(pastValues) > self.pastValues[name]["n"]):
      pastValues.pop(0)

    sum = 0
    for val in pastValues:
      sum += val
    avg = sum / len(pastValues)

    m = 2.0 / (range["top"]- range["bottom"])
    b = 1 - (m*range["top"])
    normalized =  (m*avg) + b
    normalized = max(min(normalized, 0.999), -0.999)

    snapped = normalized
    def getValue(n):
      if n > 0:
        return math.floor(n * (maxSteps + 1))
      else:
        return math.ceil(n * (maxSteps + 1))
    
    value = getValue(snapped)
    snap = (1.0 / (maxSteps + 1)) * self.gyroSnap
    if value == self.state[name] + 1:
      snapped -= snap
      value = getValue(snapped)
    if value == self.state[name] - 1:
      snapped += snap
      value = getValue(snapped)
    
    self.state[name] = value
    return value, normalized

  async def findController(self):
    while (not self.controllerFound):
      self.controllerFound = False
      devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
      for device in devices:
        if (device.name == "Wireless Controller"):
          self.buttons = evdev.InputDevice(device.path)
          self.controllerFound = True
        elif (device.name == "Wireless Controller Motion Sensors"):
          self.motion = evdev.InputDevice(device.path)
        elif (device.name == "Wireless Controller Touchpad"):
          self.touch = evdev.InputDevice(device.path)

      if (self.controllerFound):
        asyncio.ensure_future(self.motionLoop())
        asyncio.ensure_future(self.buttonsLoop())
        asyncio.ensure_future(self.touchLoop())

  async def motionLoop(self):
    async for event in self.motion.async_read_loop():
      if event.code == self.motionCodes["x"]:
        intValue, value = self.processValue(event.value, "gyroX", self.midiShock.inversionRange)
        self.midiShock.setInversion(intValue)
        self.gyroThumbValue = value
      elif event.code == self.motionCodes["z"]:
        t = time.time()
        if event.value != 0 and (t - self.lastMidiUpdate) > self.midiMessageRate:
          max = self.ranges["gyroZ"]["bottom"]
          value = math.floor((min(abs(event.value), max) / max)*127)
          self.midiShock.setAfterTouch(value)
          self.lastMidiUpdate = t
  
  async def buttonsLoop(self):
    async for event in self.buttons.async_read_loop():
      forceUpdate = True
      if event.type == evdev.ecodes.EV_KEY:
        for button in ["ex", "circle", "triangle", "square"]:
          if event.code == self.buttonCodes[button]:
            if event.value == 1:
              self.midiShock.playChord(button)
            elif self.midiShock.activeChord == button:
              self.midiShock.stopChord()
        if event.code == self.buttonCodes["lt2"]:
          if event.value == 1:
            self.midiShock.playBass()
          else:
            self.midiShock.stopBass()
        elif event.code == self.buttonCodes["rt2"]:
          if event.value == 1:
            self.midiShock.setAlternate(True)
          else:
            self.midiShock.setAlternate(False)
        elif event.code == self.buttonCodes["lt"]:
          if event.value == 1:
            self.state["lt"] = True
            self.midiShock.setModulation("left")
          else:
            self.state["lt"] = False
            if self.state["rt"]:
              self.midiShock.setModulation("right")
            else:
              self.midiShock.setModulation("none")
        elif event.code == self.buttonCodes["rt"]:
          if event.value == 1:
            self.state["rt"] = True
            self.midiShock.setModulation("right")
          else:
            self.state["rt"] = False
            if self.state["lt"]:
              self.midiShock.setModulation("left")
            else:
              self.midiShock.setModulation("none")
        elif event.code == self.buttonCodes["options"]:
          if event.value == 1:
            self.midiShock.toggleShift()
        elif event.code == self.buttonCodes["share"]:
          if event.value == 1:
            self.midiShock.toggleAlt()
      elif event.type == evdev.ecodes.EV_ABS:
        if event.code == self.absCodes["lJoyY"]:
          intValue, value = self.processValue(event.value, "lJoyY", self.midiShock.bassRange)
          self.midiShock.setBassPosition(intValue)
          self.lJoyYThumbValue = value
          forceUpdate = False
        if event.code == 16:
          if event.value == -1:
            self.midiShock.setSecondary("left")
          elif event.value == 0:
            self.midiShock.setSecondary("none")
          elif event.value == 1:
            self.midiShock.setSecondary("right")
        elif event.code == 17:
          if not self.midiShock.shift and not self.midiShock.alt:
            if event.value == -1:
              self.midiShock.incrementSpread()
            elif event.value == 1:
              self.midiShock.decrementSpread()
          elif self.midiShock.shift and not self.midiShock.alt:
            if event.value == -1:
              self.midiShock.incrementKey()
            elif event.value == 1:
              self.midiShock.decrementKey()
          elif not self.midiShock.shift and self.midiShock.alt:
            if event.value == -1:
              self.midiShock.incrementSetting()
            elif event.value == 1:
              self.midiShock.decrementSetting()

      if (forceUpdate):
        self.midiShock.updateDisplay()

  async def touchLoop(self):
    async for event in self.touch.async_read_loop():
      print("touch")
      print(evdev.categorize(event))