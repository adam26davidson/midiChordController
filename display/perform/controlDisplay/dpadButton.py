from models.appParameter import AppParameter
from .controlButton import ControlButton
from .constants import ACTIVE_COLOR, INACTIVE_COLOR, FONT

class DPadButton(ControlButton):

    radius = 2.5

    def __init__(self, master, param: AppParameter, type: str, direction, centerX, centerY):
        super().__init__(master)
        self.master = master

        self.centerX = centerX
        self.centerY = centerY
        self.direction = direction

        self.setParam(param, type, False)

        self.drawButton()

    def setParam(self, param: AppParameter, type: str, update: bool = True):
        self.param = param
        self.type = type
        if not param:
            self.label = "∅"
        else:
            if type == "POLAR":
                if self.direction == "LEFT" or self.direction == "DOWN":
                    self.label = f"-{param.labelAbreviation}"
                else:
                    self.label = f"+{param.labelAbreviation}"
            else:
                self.label = param.labelAbreviation

        if update:
            self.master.itemconfig(self.textObject, text=self.label)

    def drawButton(self):
        cX = self.centerX
        cY = self.centerY

        if (self.direction == "LEFT"):
            xl1 = cX - self.radius
            xl2 = xl1 + 1
            xl3 = xl2 + 1
            xlt = xl1 + 0.75
            self.drawButtonFromParams(xl1, cY+1, xl2, cY+1, xl3, cY, xl2, cY-1, xl1, cY-1, xlt, cY)
        elif (self.direction == "RIGHT"):
            xr1 = cX + self.radius
            xr2 = xr1 - 1
            xr3 = xr2 - 1
            xrt = xr1 - 0.75
            self.drawButtonFromParams(xr1, cY+1, xr2, cY+1, xr3, cY, xr2, cY-1, xr1, cY-1, xrt, cY)
        elif (self.direction == "UP"):
            yt1 = cY - self.radius
            yt2 = yt1 + 1
            yt3 = yt2 + 1
            ytt = yt1 + 0.75
            self.drawButtonFromParams(cX-1, yt1, cX-1, yt2, cX, yt3, cX+1, yt2, cX+1, yt1, cX, ytt)
        elif (self.direction == "DOWN"):
            yb1 = cY + self.radius
            yb2 = yb1 - 1
            yb3 = yb2 - 1
            ybt = yb1 - 0.75
            self.drawButtonFromParams(cX-1, yb1, cX-1, yb2, cX, yb3, cX+1, yb2, cX+1, yb1, cX, ybt)
    
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
            fill=INACTIVE_COLOR,
            font=FONT
        )

    def on(self):
        self.master.itemconfig(self.canvasObject, outline=ACTIVE_COLOR, fill=ACTIVE_COLOR)
        self.master.itemconfig(self.textObject, fill='#000000')

    def off(self):
        self.master.itemconfig(self.canvasObject, outline=INACTIVE_COLOR, fill="#000000")
        self.master.itemconfig(self.textObject, fill=INACTIVE_COLOR)
    