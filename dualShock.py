from midiShock import MidiShock
import evdev
import asyncio


class DualShock:
  def __init__(self, midiShock):
    self.midiShock = midiShock
    print(evdev.list_devices())
    self.state = {
      "lt": False,
      "rt": False
    }
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

  def normalize(value, range):
      b = (range["top"]- range["bottom"])/2.0
      m = range["top"] - b
      return (m*value) + b

  async def motionLoop(self):
    async for event in self.motion.async_read_loop():
      if event.code == self.motionCodes["x"]:
        value = self.normalize(event.value, self.ranges["gyroX"])
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