from midiShock import MidiShock
from dualShock import DualShock
from display.display import Display
import asyncio
import tkinter as tk

root = tk.Tk()
display = Display(root)
midiShock = MidiShock(display)

def test():
  dualShock = DualShock(midiShock)

  loop = asyncio.get_event_loop()
  loop.run_forever()

root.after(0, test)
root.mainloop()