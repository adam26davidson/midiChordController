from midiShock import MidiShock
from dualShock import DualShock
import asyncio

midiShock = MidiShock()

def test():
  dualShock = DualShock(midiShock)

  loop = asyncio.get_event_loop()
  loop.run_forever()

midiShock.display.root.after(0, test)
midiShock.display.root.mainloop()