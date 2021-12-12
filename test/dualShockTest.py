import evdev
import asyncio

print([(evdev.InputDevice(path).name, path) for path in evdev.list_devices()])

motion = None
touch = None
buttons = None

async def buttonsLoop():
  async for event in buttons.async_read_loop():
    if event.type == evdev.ecodes.EV_KEY:
      print("button")
      print(evdev.categorize(event))
      print(event)
    elif event.type == evdev.ecodes.EV_ABS:
      print(event)

async def touchLoop():
  async for event in touch.async_read_loop():
    print("touch")
    print(evdev.categorize(event))

async def motionLoop():
  async for event in motion.async_read_loop():
    print("motion")
    print(evdev.categorize(event))
      

if (evdev.list_devices().count('/dev/input/event1') == 1):
  motion = evdev.InputDevice('/dev/input/event5')
  touch = evdev.InputDevice('/dev/input/event4')
  buttons = evdev.InputDevice('/dev/input/event6')

  #asyncio.ensure_future(motionLoop())
  #asyncio.ensure_future(buttonsLoop())
  asyncio.ensure_future(touchLoop())
  
loop = asyncio.get_event_loop()
loop.run_forever()


