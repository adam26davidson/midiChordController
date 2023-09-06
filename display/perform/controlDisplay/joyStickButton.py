from .controlButton import ControlButton
from .constants import ACTIVE_COLOR, INACTIVE_COLOR, FONT


class JoyStickButton(ControlButton):

    radius = 1.4
    textRadius = 0.7

    def __init__(self, master, lLabel, rLabel, tLabel, bLabel, cLabel, centerX, centerY, side):
        super().__init__(master)
        self.master = master
        self.leftLabel = lLabel
        self.rightLabel = rLabel
        self.topLabel = tLabel
        self.bottomLabel = bLabel
        self.clickLabel = cLabel
        self.centerX = centerX
        self.centerY = centerY
        self.side = side
        
        self.drawButton()

    def drawButton(self):
        uToC = self.master.unitsToCoord
        r = self.radius; cx = self.centerX; cy = self.centerY
        
        self.canvasObject = self.master.create_oval(
            uToC(self.centerX - self.radius),
            uToC(self.centerY - self.radius),
            uToC(self.centerX + self.radius),
            uToC(self.centerY + self.radius),
            fill="#000000",
            outline=INACTIVE_COLOR,
            width=2
        )

        self.rightTextBackgroundObject , self.rightTextObject = self.drawTextAndBackground(self.rightLabel, cx + r, cy)
        self.leftTextBackgroundObject , self.leftTextObject = self.drawTextAndBackground(self.leftLabel, cx - r, cy)  
        self.topTextBackgroundObject , self.topTextObject = self.drawTextAndBackground(self.topLabel, cx, cy - r)
        self.bottomTextBackgroundObject , self.bottomTextObject = self.drawTextAndBackground(self.bottomLabel, cx, cy + r)

        yl = cy + r
        if self.side == "LEFT":
            l = f"{self.clickLabel} ↓"
            self.clickTextBackgroundObject , self.clickTextObject = self.drawTextAndBackground(l, cx - (r + 1), yl) 
        else:
            l = f"↓ {self.clickLabel}"
            self.clickTextBackgroundObject , self.clickTextObject = self.drawTextAndBackground(l, cx + (r + 1), yl)


    def drawTextAndBackground(self, label, centerX, centerY):
        uToC = self.master.unitsToCoord
        backgroundObject = self.master.create_oval(
            uToC(centerX - self.textRadius),
            uToC(centerY - self.textRadius),
            uToC(centerX + self.textRadius),
            uToC(centerY + self.textRadius),
            fill="#000000",
            outline="#000000",
            width=2
        )

        textObject = self.master.create_text(
            uToC(centerX),
            uToC(centerY),
            text=label,
            fill=INACTIVE_COLOR,
            font=FONT
        )

        return backgroundObject, textObject
    