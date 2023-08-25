from .controlButton import ControlButton
from .constants import ACTIVE_COLOR, INACTIVE_COLOR, FONT


class CircularButton(ControlButton):

    def __init__(self, master, label, centerX, centerY, unitSize):
        super().__init__(master, label)
        self.master = master
        self.label = label
        self.centerX = centerX
        self.centerY = centerY
        self.unitSize = unitSize
        self.radius = unitSize

        self.drawButton()

    def drawButton(self):
        self.canvasObject = self.master.create_oval(
            self.centerX - self.radius,
            self.centerY - self.radius,
            self.centerX + self.radius,
            self.centerY + self.radius,
            fill="#000000",
            outline=INACTIVE_COLOR,
            width=2
        )

        self.textObject = self.master.create_text(
            self.centerX,
            self.centerY,
            text=self.label,
            fill="#ffffff",
            font=FONT
        )
    