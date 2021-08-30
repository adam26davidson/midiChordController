import evdev
from evdev import InputDevice, categorize, ecodes
import asyncio

class DualShock:
  def __init__(self, sliders):
    print(evdev.list_devices())
    self.values = {}
    self.ranges = {
      "gyroXRange": {"top": -8050, "bottom": 8050},
      0:{"min":0, "max":0},
      1:{"min":0, "max":0},
      2:{"min":0, "max":0},
      3:{"min":0, "max":0},
      4:{"min":0, "max":0},
      5:{"min":0, "max":0}
    }
    if (evdev.list_devices().count('/dev/input/event1') == 1):
      self.motion = InputDevice('/dev/input/event1')
      self.touch = InputDevice('/dev/input/event0')
      self.buttons = InputDevice('/dev/input/event2')

      asyncio.ensure_future(self.motionLoop(sliders))
      asyncio.ensure_future(self.buttonsLoop())
      asyncio.ensure_future(self.touchLoop())

  async def motionLoop(self, sliders):
    async for event in self.motion.async_read_loop():
      self.values[event.code] = event.value
      if event.value < self.ranges[event.code]["min"]:
          self.ranges[event.code]["min"] = event.value
      if event.value > self.ranges[event.code]["max"]:
          self.ranges[event.code]["max"] = event.value
      if event.code == 0:
        print(event.value)
      sliders.positionThumb(self.values, self.ranges, event.code)
  
  async def buttonsLoop(self):
    async for event in self.buttons.async_read_loop():
      if event.type == evdev.ecodes.EV_KEY:
        print("button")
        print(evdev.categorize(event))

  async def touchLoop(self):
    async for event in self.touch.async_read_loop():
      print("touch")
      print(evdev.categorize(event))
      

