from midiShock import MidiShock
import evdev
import asyncio
import math


class DualShock:
  def __init__(self, midiShock):
    self.midiShock = midiShock
    print(evdev.list_devices())
    self.state = {
      "lt": False,
      "rt": False,
      "gyroX": 0
    }
    self.pastValues = {"gyroX": {"n": 4, "values": []}}
    self.gyroSnap = 0.3
    self.buttonCodes = {"ex": 304, "square": 308, "triangle": 307, "circle": 305, "rt": 311, "rt2": 313, "lt": 310, "lt2": 312}
    self.motionCodes = {"x": 2, "z": 0}
    self.ranges = {
      "gyroX": {"top": -8050, "bottom": 8050},
    }
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

    def getValue(n):
      if n > 0:
        return math.floor(n * maxSteps)
      else:
        return math.ceil(n * maxSteps)
    
    value = getValue(normalized)
    snap = (1.0 / maxSteps) * self.gyroSnap
    if value == self.state[name] + 1:
      normalized -= snap
      value = getValue(normalized)
    if value == self.state[name] - 1:
      normalized += snap
      value = getValue(normalized)
    
    self.state[name] = value
    return value

  async def motionLoop(self):
    async for event in self.motion.async_read_loop():
      if event.code == self.motionCodes["x"]:
        value = self.processValue(event.value, "gyroX", self.midiShock.inversionRange)
        self.midiShock.setInversion(value)
      self.midiShock.updateDisplay()
  
  async def buttonsLoop(self):
    async for event in self.buttons.async_read_loop():
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
      elif event.type == evdev.ecodes.EV_ABS:
        if event.code == 17:
          if event.value == -1:
            self.midiShock.incrementSpread()
          elif event.value == 1:
            self.midiShock.decrementSpread()

      self.midiShock.updateDisplay()


  async def touchLoop(self):
    async for event in self.touch.async_read_loop():
      print("touch")
      print(evdev.categorize(event))
      self.midiShock.updateDisplay()