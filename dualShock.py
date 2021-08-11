import evdev
from evdev import InputDevice, categorize, ecodes
import time

class DualShock:
  def __init__(self, sliders):
    print(evdev.list_devices())
    self.values = {}
    self.ranges = {
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

      self.readLoop(sliders)

  def readLoop(self, sliders):
    while 1:
      for event in self.motion.read():
        if event.type == ecodes.ABS_RX:
          self.values[event.code] = event.value
          if event.value < self.ranges[event.code]["min"]:
              self.ranges[event.code]["min"] = event.value
          if event.value > self.ranges[event.code]["max"]:
              self.ranges[event.code]["max"] = event.value
          sliders.positionThumb(self.values, self.ranges, event.code)

      for event in self.buttons.read():
        print(event)

      for event in self.touch.read():
        print(event)
