from midiShock import MidiShock
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
    self.buttonCodes = {"ex": 304, "square": 308, "triangle": 307, "circle": 305, "rt": 311, "rt2": 313, "lt": 310, "lt2": 312, "options": 315}
    self.absCodes = {"padX": 16, "padY": 17, "lJoyX": 0, "lJoyY": 1, "rJoyX": 3, "rJoyY": 4}
    self.motionCodes = {"x": 2, "z": 0}
    self.ranges = {
      "gyroX": {"top": -8050, "bottom": 8050},
      "lJoyY": {"top": 0, "bottom": 255},
    }
    self.lastUpdate = time.time()
    if (evdev.list_devices().count('/dev/input/event1') == 1):
      self.motion = evdev.InputDevice('/dev/input/event1')
      self.touch = evdev.InputDevice('/dev/input/event0')
      self.buttons = evdev.InputDevice('/dev/input/event2')

      asyncio.ensure_future(self.motionLoop())
      asyncio.ensure_future(self.buttonsLoop())
      asyncio.ensure_future(self.touchLoop())

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

  def updateDisplay(self, force=False):
    t = time.time()
    if t - self.lastUpdate > ANIMATION_STEP:
      self.midiShock.display.setInversionThumb(self.gyroThumbValue)
      self.midiShock.display.setBassPositionThumb(self.lJoyYThumbValue)
      self.midiShock.updateDisplay()
    elif force:
      self.midiShock.updateDisplay()

  async def motionLoop(self):
    async for event in self.motion.async_read_loop():
      if event.code == self.motionCodes["x"]:
        intValue, value = self.processValue(event.value, "gyroX", self.midiShock.inversionRange)
        self.midiShock.setInversion(intValue)
        self.gyroThumbValue = value
      self.updateDisplay()
  
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
      elif event.type == evdev.ecodes.EV_ABS:
        if event.code == self.absCodes["lJoyY"]:
          intValue, value = self.processValue(event.value, "lJoyY", self.midiShock.bassRange)
          self.midiShock.setBassPosition(intValue)
          self.lJoyYThumbValue = value
          forceUpdate = False
        if not self.midiShock.shift:
          if event.code == 17:
            if event.value == -1:
              self.midiShock.incrementSpread()
            elif event.value == 1:
              self.midiShock.decrementSpread()
          elif event.code == 16:
            if event.value == -1:
              self.midiShock.setSecondary("left")
            elif event.value == 0:
              self.midiShock.setSecondary("none")
            elif event.value == 1:
              self.midiShock.setSecondary("right")
        else:
          if event.code == 17:
            if event.value == -1:
              self.midiShock.incrementKey()
            elif event.value == 1:
              self.midiShock.decrementKey()
          elif event.code == 16:
            if event.value == -1:
              self.midiShock.setSecondary("left")
            elif event.value == 0:
              self.midiShock.setSecondary("none")
            elif event.value == 1:
              self.midiShock.setSecondary("right")

      self.updateDisplay(force=forceUpdate)

  async def touchLoop(self):
    async for event in self.touch.async_read_loop():
      print("touch")
      print(evdev.categorize(event))
      self.updateDisplay()