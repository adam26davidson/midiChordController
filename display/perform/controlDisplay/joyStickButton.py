from .controlButton import ControlButton
from .constants import ACTIVE_COLOR, INACTIVE_COLOR, FONT


class JoyStickButton(ControlButton):

    radius = 1.4
    textRadius = 0.5

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

        self.rightTextBackgroundObject , self.rightTextObject = self.drawTextAndBackground(self.rightLabel, self.centerX + self.radius, self.centerY)
        self.leftTextBackgroundObject , self.leftTextObject = self.drawTextAndBackground(self.leftLabel, self.centerX - self.radius, self.centerY)  
        self.topTextBackgroundObject , self.topTextObject = self.drawTextAndBackground(self.topLabel, self.centerX, self.centerY - self.radius)
        self.bottomTextBackgroundObject , self.bottomTextObject = self.drawTextAndBackground(self.bottomLabel, self.centerX, self.centerY + self.radius)

    def drawTextAndBackground(self, label, centerX, centerY):
        uToC = self.master.unitsToCoord
        backgroundObject = self.master.create_oval(
            uToC(centerX - self.textRadius),
            uToC(centerY - self.textRadius),
            uToC(centerX + self.textRadius),
            uToC(centerY + self.textRadius),
            fill="#000000",
            outline=INACTIVE_COLOR,
            width=2
        )

        textObject = self.master.create_text(
            uToC(centerX),
            uToC(centerY),
            text=label,
            fill="#ffffff",
            font=FONT
        )

        return backgroundObject, textObject
    