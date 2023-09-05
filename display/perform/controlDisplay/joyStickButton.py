from .controlButton import ControlButton
from .constants import ACTIVE_COLOR, INACTIVE_COLOR, FONT


class JoyStickButton(ControlButton):

    radius = 1.5

    def __init__(self, master, lLabel, rLabel, tLabel, bLabel, centerX, centerY):
        super().__init__(master)
        self.master = master
        self.leftLabel = lLabel
        self.rightLabel = rLabel
        self.topLabel = tLabel
        self.bottomLabel = bLabel
        self.centerX = centerX
        self.centerY = centerY
        
        self.drawButton()

    def drawButton(self):
        uToC = self.master.unitsToCoord
        
        self.canvasObject = self.master.create_oval(
            uToC(self.centerX - self.radius),
            uToC(self.centerY - self.radius),
            uToC(self.centerX + self.radius),
            uToC(self.centerY + self.radius),
            fill="#000000",
            outline=INACTIVE_COLOR,
            width=2
        )

        self.rightTextObject = self.master.create_text(
            uToC(self.centerX + self.radius),
            uToC(self.centerY),
            text=self.rightLabel,
            fill="#ffffff",
            bg="#000000",
            font=FONT
        )

        self.leftTextObject = self.master.create_text(
            uToC(self.centerX - self.radius),
            uToC(self.centerY),
            text=self.leftLabel,
            fill="#ffffff",
            bg="#000000",
            font=FONT
        )

        self.topTextObject = self.master.create_text(
            uToC(self.centerX),
            uToC(self.centerY - self.radius),
            text=self.topLabel,
            fill="#ffffff",
            bg="#000000",
            font=FONT
        )

        self.bottomTextObject = self.master.create_text(
            uToC(self.centerX),
            uToC(self.centerY + self.radius),
            text=self.bottomLabel,
            fill="#ffffff",
            bg="#000000",
            font=FONT
        )
    