from .controlButton import ControlButton
from .constants import ACTIVE_COLOR, INACTIVE_COLOR, FONT


class BumperButton(ControlButton):

    width = 4
    height = 2

    def __init__(self, master, label, centerX, centerY, unitSize):
        super().__init__(master)
        self.master = master
        self.label = label
        self.centerX = centerX
        self.centerY = centerY
        self.unitSize = unitSize
        self.radius = unitSize

        self.drawButton()

    def drawButton(self):
        uToC = self.master.unitsToCoord
        self.canvasObject = self.master.create_rectangle(
            uToC(self.centerX - (self.width / 2)),
            uToC(self.centerY - (self.height / 2)),
            uToC(self.centerX + (self.width / 2)),
            uToC(self.centerY + (self.height / 2)),
            fill="#000000",
            outline=INACTIVE_COLOR,
            width=2
        )

        self.textObject = self.master.create_text(
            self.centerX,
            self.centerY,
            text=self.label,
            fill=INACTIVE_COLOR,
            font=FONT
        )