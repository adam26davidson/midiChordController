from display.display import Display
from midiShock import MidiShock
from dualShock import DualShock
import threading
import asyncio
import time

display = Display()
midiShock = MidiShock(display)

sides = ["left", "none", "right"]

def test():
  dualShock = DualShock(midiShock)
  loop = asyncio.get_event_loop()
  loop.run_forever()

  # midiShock.playChord("ex")
  # midiShock.setKey(2)
  # midiShock.setSpread(6)
  # midiShock.setAlternate(True)
  # midiShock.setModulation("left")
  # midiShock.setSecondary("left")
  # for i in range(1, 20):
  #   time.sleep(0.5)
  #   midiShock.setSpread(i)


# t = threading.Thread(target=test)
# t.daemon = True
# t.start()

display.root.after(0, test)
display.root.mainloop()

# global dualShock = DualShock() 

# global loop = asyncio.get_event_loop()
# loop.run_forever()




