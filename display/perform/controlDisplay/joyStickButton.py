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
        
        self.setXParams(xParams, xType, False)
        self.setYParams(yParams, yType, False)

        self.clickLabel = "∅" if not cParam else cParam.labelAbreviation
        self.centerX = centerX
        self.centerY = centerY
        self.side = side
        
        self.drawButton()

    def setXParams(self, params: List[AppParameter], type: str, update: bool = True):
        self.setAxisParams(params, type, "X", update)

    def setYParams(self, params: List[AppParameter], type: str, update: bool = True):
        self.setAxisParams(params, type, "Y", update)

    def setAxisParams(self, params: List[AppParameter], type: str, axis: str, update: bool = True):
        if axis == "X":
            self.xParams = params
            self.xType = type
        else:
            self.yParams = params
            self.yType = type
        
        if (len(params) == 0):
            if axis == "X":
                self.leftLabel = "∅"
                self.rightLabel = "∅"
            else:
                self.topLabel = "∅"
                self.bottomLabel = "∅"
        else:
            if type == "ANALOG" or type == "POLAR":
                if axis == "X":
                    self.leftLabel = f"-{params[0].labelAbreviation}"
                    self.rightLabel = f"+{params[0].labelAbreviation}"
                else:
                    self.topLabel = f"+{params[0].labelAbreviation}"
                    self.bottomLabel = f"-{params[0].labelAbreviation}"
            else:
                if axis == "X":
                    self.leftLabel = params[0].labelAbreviation
                    self.rightLabel = params[1].labelAbreviation
                else:
                    self.topLabel = params[0].labelAbreviation
                    self.bottomLabel = params[1].labelAbreviation

        if update:
            if axis == "X":
                self.master.itemconfig(self.leftTextObject, text=self.leftLabel)
                self.master.itemconfig(self.rightTextObject, text=self.rightLabel)
            else:
                self.master.itemconfig(self.topTextObject, text=self.topLabel)
                self.master.itemconfig(self.bottomTextObject, text=self.bottomLabel)


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
        self.master.itemconfig(self.leftTextBackgroundObject, fill=ACTIVE_COLOR, outline=ACTIVE_COLOR)
        self.master.itemconfig(self.leftTextObject, fill="#000000")
    
    def left_off(self):
        self.master.itemconfig(self.leftTextBackgroundObject, fill="#000000", outline=INACTIVE_COLOR)
        self.master.itemconfig(self.leftTextObject, fill=INACTIVE_COLOR)

    def right_on(self):
        self.master.itemconfig(self.rightTextBackgroundObject, fill=ACTIVE_COLOR, outline=ACTIVE_COLOR)
        self.master.itemconfig(self.rightTextObject, fill="#000000")

    def right_off(self):
        self.master.itemconfig(self.rightTextBackgroundObject, fill="#000000", outline=INACTIVE_COLOR)
        self.master.itemconfig(self.rightTextObject, fill=INACTIVE_COLOR)

    def up_on(self):
        self.master.itemconfig(self.topTextBackgroundObject, fill=ACTIVE_COLOR, outline=ACTIVE_COLOR)
        self.master.itemconfig(self.topTextObject, fill="#000000")

    def up_off(self):
        self.master.itemconfig(self.topTextBackgroundObject, fill="#000000", outline=INACTIVE_COLOR)
        self.master.itemconfig(self.topTextObject, fill=INACTIVE_COLOR)

    def down_on(self):
        self.master.itemconfig(self.bottomTextBackgroundObject, fill=ACTIVE_COLOR, outline=ACTIVE_COLOR)
        self.master.itemconfig(self.bottomTextObject, fill="#000000")

    def down_off(self):
        self.master.itemconfig(self.bottomTextBackgroundObject, fill="#000000", outline=INACTIVE_COLOR)
        self.master.itemconfig(self.bottomTextObject, fill=INACTIVE_COLOR)

    def update_x(self, value):
        pass

    def update_y(self, value):
        pass
        
    