import tkinter 
from display.display import Display
from midiShock import MidiShock
from dualShock import DualShock
import asyncio
import time

display = Display()
midiShock = MidiShock(display)

def test():
  dualShock = DualShock(midiShock)

  loop = asyncio.get_event_loop()
  loop.run_forever()

display.root.after(0, test)
display.root.mainloop()

# t = threading.Thread(target=test)
# t.daemon = True
# t.start()


# global dualShock = DualShock() 

# global loop = asyncio.get_event_loop()
# loop.run_forever()




