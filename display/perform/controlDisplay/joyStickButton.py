from typing import List
from models.appParameter import AppParameter
from .controlButton import ControlButton
from .constants import ACTIVE_COLOR, INACTIVE_COLOR, FONT


class JoyStickButton(ControlButton):

    radius = 1.4
    textRadius = 0.7

    def __init__(self, master, 
                 xParams: List[AppParameter], 
                 yParams: List[AppParameter],
                 xType: str,
                 yType: str,
                 cParam: AppParameter, 
                 centerX, centerY, side):
        super().__init__(master)
        self.master = master
        self.xParams = xParams
        self.yParams = yParams
        self.xType = xType
        self.yType = yType

        if (len(xParams) == 0):
            self.leftLabel = "∅"
            self.rightLabel = "∅"
        else:
            if xType == "ANALOG" or xType == "POLAR":
                self.leftLabel = f"-{xParams[0].labelAbreviation}"
                self.rightLabel = f"+{xParams[0].labelAbreviation}"
            else:
                self.leftLabel = xParams[0].labelAbreviation
                self.rightLabel = xParams[1].labelAbreviation

        if (len(yParams) == 0):
            self.topLabel = "∅"
            self.bottomLabel = "∅"
        else:
            if yType == "ANALOG" or yType == "POLAR":
                self.topLabel = f"+{yParams[0].labelAbreviation}"
                self.bottomLabel = f"-{yParams[0].labelAbreviation}"
            else:
                self.topLabel = yParams[0].labelAbreviation
                self.bottomLabel = yParams[1].labelAbreviation

        self.clickLabel = cParam.labelAbreviation
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
            self.arrowObject = self.drawTextForClick("↓", cx - (r + 0.5), yl)
            self.clickTextObject = self.drawTextForClick(self.clickLabel, cx - (r + 1.1), yl) 
        else:
            self.arrowObject = self.drawTextForClick("↓", cx + (r + 0.5), yl)
            self.clickTextObject = self.drawTextForClick(self.clickLabel, cx + (r + 1.1), yl)


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

    def drawTextForClick(self, label, centerX, centerY):
        uToC = self.master.unitsToCoord
        return self.master.create_text(
            uToC(centerX),
            uToC(centerY),
            text=label,
            fill=INACTIVE_COLOR,
            font=FONT
        )
    
    def button_on(self):
        self.master.itemconfig(self.arrowObject, fill=ACTIVE_COLOR)
        self.master.itemconfig(self.clickTextObject, fill=ACTIVE_COLOR)

    def button_off(self):
        self.master.itemconfig(self.arrowObject, fill=INACTIVE_COLOR)
        self.master.itemconfig(self.clickTextObject, fill=INACTIVE_COLOR)

    def left_on(self):
        self.master.itemconfig(self.leftTextBackgroundObject, outline=ACTIVE_COLOR)
        self.master.itemconfig(self.leftTextObject, fill="#000000")
    
    def left_off(self):
        self.master.itemconfig(self.leftTextBackgroundObject, outline=INACTIVE_COLOR)
        self.master.itemconfig(self.leftTextObject, fill=INACTIVE_COLOR)

    def right_on(self):
        self.master.itemconfig(self.rightTextBackgroundObject, outline=ACTIVE_COLOR)
        self.master.itemconfig(self.rightTextObject, fill="#000000")

    def right_off(self):
        self.master.itemconfig(self.rightTextBackgroundObject, outline=INACTIVE_COLOR)
        self.master.itemconfig(self.rightTextObject, fill=INACTIVE_COLOR)

    def up_on(self):
        self.master.itemconfig(self.topTextBackgroundObject, outline=ACTIVE_COLOR)
        self.master.itemconfig(self.topTextObject, fill="#000000")

    def up_off(self):
        self.master.itemconfig(self.topTextBackgroundObject, outline=INACTIVE_COLOR)
        self.master.itemconfig(self.topTextObject, fill=INACTIVE_COLOR)

    def down_on(self):
        self.master.itemconfig(self.bottomTextBackgroundObject, outline=ACTIVE_COLOR)
        self.master.itemconfig(self.bottomTextObject, fill="#000000")

    def down_off(self):
        self.master.itemconfig(self.bottomTextBackgroundObject, outline=INACTIVE_COLOR)
        self.master.itemconfig(self.bottomTextObject, fill=INACTIVE_COLOR)

    def updateX(self):
        pass

    def updateY(self):
        pass
        
    