from .controlButton import ControlButton
from .constants import ACTIVE_COLOR, INACTIVE_COLOR, FONT


class TriggerButton(ControlButton):

    width = 4
    height = 1.5
    radius = 0.75

    def __init__(self, master, label, centerX, centerY):
        super().__init__(master)
        self.master = master
        self.label = label
        self.centerX = centerX
        self.centerY = centerY

        self.drawButton()

    def drawButton(self):
        uToC = self.master.unitsToCoord
        r = self.radius

        xl = self.centerX - (self.width / 2)
        xm1 = xl + r
        xm2 = (self.centerX + (self.width / 2)) - r
        xr = self.centerX + (self.width / 2)

        yt = self.centerY - (self.height / 2)
        ym = yt + r
        yb = self.centerY + (self.height / 2)

        self.arc1 = self.master.create_arc(
            uToC(xl) - 1, uToC(yt) + 1, 
            uToC(xm1), uToC(ym + r), 
            start=180, extent=-100, 
            fill="", 
            outline=INACTIVE_COLOR, 
            width=2, 
            style="arc")
        
        self.arc2 = self.master.create_arc(
            uToC(xm2 - r), uToC(yt), 
            uToC(xr), uToC(ym + r), 
            start=0, extent=90, 
            fill="", 
            outline=INACTIVE_COLOR, 
            width=2, 
            style="arc")

        self.line1 = self.master.create_line(uToC(xm1), uToC(yt), uToC(xm2), uToC(yt), fill=INACTIVE_COLOR, width=2)
        self.line2 = self.master.create_line(uToC(xl), uToC(ym), uToC(xl), uToC(yb), fill=INACTIVE_COLOR, width=2)
        self.line3 = self.master.create_line(uToC(xl), uToC(yb), uToC(xr), uToC(yb), fill=INACTIVE_COLOR, width=2)
        self.line4 = self.master.create_line(uToC(xr), uToC(ym), uToC(xr), uToC(yb), fill=INACTIVE_COLOR, width=2)

        self.textObject = self.master.create_text(
            uToC(self.centerX),
            uToC(self.centerY),
            text=self.label,
            fill=INACTIVE_COLOR,
            font=FONT
        )