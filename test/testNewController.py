import asyncio

import evdev

print([(evdev.InputDevice(path).uniq, evdev.InputDevice(path).name) for path in evdev.list_devices()])

motion = None
touch = None
buttons = None

async def buttons_loop():
  async for event in buttons.async_read_loop():
    if event.type == evdev.ecodes.EV_KEY:
      print("button")
      print(evdev.categorize(event))
      print(event)
    elif event.type == evdev.ecodes.EV_ABS:
      pass
      #print(event)

async def touch_loop():
  async for event in touch.async_read_loop():
    if event.type == evdev.ecodes.EV_KEY or (event.type == evdev.ecodes.EV_ABS and event.code in [0, 1]):
      pass
      #print(event)

async def motion_loop():
  async for _event in motion.async_read_loop():
    pass
    # print("motion")
    # print(evdev.categorize(event))

if (evdev.list_devices().count('/dev/input/event1') == 1):
  motion = evdev.InputDevice('/dev/input/event5')
  touch = evdev.InputDevice('/dev/input/event4')
  buttons = evdev.InputDevice('/dev/input/event6')

  #asyncio.ensure_future(motion_loop())
  #asyncio.ensure_future(buttons_loop())
  _task = asyncio.ensure_future(touch_loop())

loop = asyncio.get_event_loop()
loop.run_forever()

