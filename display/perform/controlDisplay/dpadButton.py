from .controlButton import ControlButton
from .constants import ACTIVE_COLOR, INACTIVE_COLOR, FONT

class DPadButton(ControlButton):

    def __init__(self, master, label, direction, unitSize):
        super().__init__(master)
        self.master = master
        self.label = label
        self.direction = direction
        self.unitSize = unitSize
        self.radius = unitSize

        self.drawButton()

    def drawButton(self):
        cX = 3
        cY = 9
        if (self.direction == "LEFT"):
            self.drawButtonFromParams(cX-3, cY+1, cX-2, cY+1, cX-1, cY, cX-2, cY-1, cX-3, cY-1, 0.75, 9)
        elif (self.direction == "RIGHT"):
            self.drawButtonFromParams(cX+3, cY+1, cX+2, cY+1, cX+1, cY, cX+2, cY-1, cX+3, cY-1, 5.25, 9)
        elif (self.direction == "UP"):
            self.drawButtonFromParams(cX-1, cY-3, cX-1, cY-2, cX, cY-1, cX+1, cY-2, cX+1, cY-3, 3, 6.75)
        elif (self.direction == "DOWN"):
            self.drawButtonFromParams(cX-1, cY+3, cX-1, cY+2, cX, cY+1, cX+1, cY+2, cX+1, cY+3, 3, 11.25)
    
    def drawButtonFromParams(self, x1, y1, x2, y2, x3, y3, x4, y4, x5, y5, tx, ty):
        uToC = self.master.unitsToCoord
        self.canvasObject = self.master.create_polygon(
            uToC(x1), uToC(y1),
            uToC(x2), uToC(y2),
            uToC(x3), uToC(y3),
            uToC(x4), uToC(y4),
            uToC(x5), uToC(y5),
            fill="#000000",
            outline=INACTIVE_COLOR,
            width=2
        )
        self.textObject = self.master.create_text(
            uToC(tx),
            uToC(ty),
            text=self.label,
            fill="#ffffff",
            font=FONT
        )

    