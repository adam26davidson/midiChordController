import asyncio
import tkinter as tk

from dualShockTest import DualShock


class Sliders(tk.Canvas):
    def __init__(self, master=None):
        super().__init__(master, width=800, height=480, bd=0, relief="flat", bg="#ffffff")
        self.master = master
        self.thumbs = self.drawSliders()
        self.pack()

    def drawSliders(self):
        thumbs = []
        for i in range(6):
            #draw tracks
            sX = 115 + (114*i)
            sY = 40
            eX = 115 + (114*i)
            eY = 440
            self.create_line(sX, sY, eX, eY)

            #draw thumbs
            y = 240
            x1 = 115 + (114*i) - 10
            x2 = 115 + (114*i) + 10
            thumbs.append(self.create_line(x1, y, x2, y))

        return thumbs

    def positionThumb(self, values, ranges, i):
        y = ((400 / (ranges[i]["max"] - ranges[i]["min"])) * values[i]) + 240
        x1 = 115 + (114*i) - 10
        x2 = 115 + (114*i) + 10
        self.coords(self.thumbs[i], x1, y, x2, y)
        self.master.update()


window = tk.Tk()
sliders = Sliders(window)

def startDS():
    DualShock(sliders)

    loop = asyncio.get_event_loop()
    loop.run_forever()

window.after(0, startDS)
window.mainloop()
