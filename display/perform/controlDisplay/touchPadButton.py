from .controlButton import ControlButton
from .constants import ACTIVE_COLOR, INACTIVE_COLOR, FONT


class TouchPadButton(ControlButton):

    width = 4
    height = 3

    def __init__(self, master, xLabel, yLabel, centerX, centerY):
        super().__init__(master)
        self.master = master
        self.xLabel = xLabel
        self.yLabel = yLabel
        self.centerX = centerX
        self.centerY = centerY

        self.drawButton()

    def drawButton(self):
        uToC = self.master.unitsToCoord
        xl = self.centerX - (self.width / 2)
        xr = self.centerX + (self.width / 2)
        yt = self.centerY - (self.height / 2)
        yb = self.centerY + (self.height / 2)

        self.canvasObject = self.master.create_rectangle(
            uToC(xl), uToC(yt), uToC(xr), uToC(yb),
            fill="#000000",
            outline=INACTIVE_COLOR,
            width=2
        )

        self.xTextObject = self.master.create_text(
            uToC(self.centerX),
            uToC(self.centerY),
            text=f"x: {self.xLabel}\ny: {self.yLabel}",
            fill=INACTIVE_COLOR,
            font=FONT
        )