from midiShock import MidiShock
from dualShock import DualShock
from display.display import Display
import asyncio
import tkinter as tk

root = tk.Tk()
display = Display(root)
midiShock = MidiShock(display)
ds = DualShock(midiShock)

loop = asyncio.get_event_loop()
loop.run_forever()