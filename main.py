from midiShock import MidiShock
from dualShock import DualShock
from display.display import Display
import asyncio
import tkinter as tk

midiShock = MidiShock()
root = tk.Tk()
display = Display(root)
midiShock.connectDisplay(display)
ds = DualShock(midiShock)

async def updateDisplay():
  while True:
    root.update()

asyncio.ensure_future(updateDisplay())

loop = asyncio.get_event_loop()
loop.run_forever()

# window = tk.Tk()
# sliders = Sliders(window)

# def startDS():
#     ds = DualShock(sliders) 

#     loop = asyncio.get_event_loop()
#     loop.run_forever()

# window.after(0, startDS)
# window.mainloop()