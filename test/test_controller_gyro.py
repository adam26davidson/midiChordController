import asyncio
import tkinter as tk

from dualShockTest import DualShock  # type: ignore[import]


class Sliders(tk.Canvas):
    def __init__(self, master=None):
        super().__init__(master, width=800, height=480, bd=0, relief="flat", bg="#ffffff")
        self.master = master  # type: ignore[assignment]
        self.thumbs = self.draw_sliders()
        self.pack()

    def draw_sliders(self):
        thumbs = []
        for i in range(6):
            #draw tracks
            s_x = 115 + (114*i)
            s_y = 40
            e_x = 115 + (114*i)
            e_y = 440
            self.create_line(s_x, s_y, e_x, e_y)

            #draw thumbs
            y = 240
            x1 = 115 + (114*i) - 10
            x2 = 115 + (114*i) + 10
            thumbs.append(self.create_line(x1, y, x2, y))

        return thumbs

    def position_thumb(self, values, ranges, i):
        y = ((400 / (ranges[i]["max"] - ranges[i]["min"])) * values[i]) + 240
        x1 = 115 + (114*i) - 10
        x2 = 115 + (114*i) + 10
        self.coords(self.thumbs[i], x1, y, x2, y)
        self.master.update()  # type: ignore[union-attr]


window = tk.Tk()
sliders = Sliders(window)

def start_ds():
    DualShock(sliders)

    loop = asyncio.get_event_loop()
    loop.run_forever()

window.after(0, start_ds)
window.mainloop()
