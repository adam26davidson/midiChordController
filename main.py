from controllers import searchForControllers
import asyncio

asyncio.ensure_future(searchForControllers())

loop = asyncio.get_event_loop()
loop.run_forever()