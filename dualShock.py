from midiShock import MidiShock
import evdev
import asyncio


class DualShock:
  def __init__(self, midiShock):
    self.midiShock = midiShock
    print(evdev.list_devices())
    self.values = {}
    self.buttonCodes = {"ex": 304, "square": 308, "triangle": 307, "circle": 305, "rt": 311, "rt2": 313, "lt": 310, "lt2": 312}
    self.ranges = {
      "gyroXRange": {"top": -8050, "bottom": 8050},
      0:{"min":0, "max":1},
      1:{"min":0, "max":1},
      2:{"min":0, "max":1},
      3:{"min":0, "max":1},
      4:{"min":0, "max":1},
      5:{"min":0, "max":1}
    }
    if (evdev.list_devices().count('/dev/input/event1') == 1):
      self.motion = evdev.InputDevice('/dev/input/event1')
      self.touch = evdev.InputDevice('/dev/input/event0')
      self.buttons = evdev.InputDevice('/dev/input/event2')

      asyncio.ensure_future(self.motionLoop())
      asyncio.ensure_future(self.buttonsLoop())
      asyncio.ensure_future(self.touchLoop())

  async def motionLoop(self):
    async for event in self.motion.async_read_loop():
      self.values[event.code] = event.value
      if event.value < self.ranges[event.code]["min"]:
          self.ranges[event.code]["min"] = event.value
      if event.value > self.ranges[event.code]["max"]:
          self.ranges[event.code]["max"] = event.value
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
            self.MidiShock.stopBass()
      self.midiShock.updateDisplay()


  async def touchLoop(self):
    async for event in self.touch.async_read_loop():
      print("touch")
      print(evdev.categorize(event))
      self.midiShock.updateDisplay()