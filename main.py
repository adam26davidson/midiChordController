from controllers import searchForControllers
from display import Display
import asyncio

display = Display()
asyncio.ensure_future(display.mainLoop())
asyncio.ensure_future(searchForControllers(display))

loop = asyncio.get_event_loop()
loop.run_forever()