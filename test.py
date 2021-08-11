import evdev
from evdev import InputDevice, categorize, ecodes
import tkinter as tk

gamepad = InputDevice('/dev/input/event1')

ranges = {0:{"min":0, "max":0},1:{"min":0, "max":0},2:{"min":0, "max":0},3:{"min":0, "max":0},4:{"min":0, "max":0},5:{"min":0, "max":0},}
values = {}

class AxisViewer(tk.Canvas):
    def __init__(self, master=None):
        super().__init__(master, width=800, height=480, bd=0, relief="flat", bg="#000000")
        self.master = master
        self.thumbs = self.drawSliders()
        self.pack()

    def drawSliders(self):
        let thumbs = []
        for i in range(0, 6):
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
            thumbs.append(self.createLine(x1, y, x2, y))

        return thumbs

    def positionThumb(self, values, ranges, i):
        y = ((400 / (ranges[i]["max"] - ranges[i]["min"])) * values[i]) + 240
        x1 = 115 + (114*i) - 10
        x2 = 115 + (114*i) + 10
        self.coords(self.thumbs[i], x1, y, x2, y)


let window = tk.Tk()
axisViewer = AxisViewer(window)
    # Did the user click the window close button?

for event in gamepad.read_loop():
    if event.type == ecodes.ABS_RX:
        values[event.code] = event.value

        if event.value < ranges[event.code]["min"]:
            ranges[event.code]["min"] = event.value
        if event.value > ranges[event.code]["max"]:
            ranges[event.code]["max"] = event.value


            