from models.appParameter import AppParameter
from .controlButton import ControlButton
from .constants import ACTIVE_COLOR, INACTIVE_COLOR, FONT


class OptionsButton(ControlButton):

    xOffset = 0.2
    yOffset = 0.2
    lineExtension = 0.05

    def __init__(self, master, param: AppParameter, centerX, centerY, unitSize):
        super().__init__(master)
        self.master = master
        self.label = "∅" if not param else param.labelAbreviation

        self.centerX = centerX
        self.centerY = centerY
        self.unitSize = unitSize
        self.radius = unitSize

        self.drawButton()

    def drawButton(self):
        uToC = self.master.unitsToCoord
        r = (1 - self.xOffset)
        arc1x1 = self.centerX - r
        arc1y1 = self.centerY - 1
        arc1x2 = self.centerX + r
        arc1y2 = arc1y1 + (2*r)
        self.arc1 = self.master.create_arc(
            uToC(arc1x1), uToC(arc1y1), 
            uToC(arc1x2), uToC(arc1y2), 
            start=0, extent=180, 
            fill="", 
            outline=INACTIVE_COLOR, 
            width=2, 
            style="arc")
        
        arc2x1 = self.centerX - r
        arc2y1 = (self.centerY + 1) - (2*r)
        arc2x2 = self.centerX + r
        arc2y2 = arc2y1 + (2*r)
        self.arc2 = self.master.create_arc(
            uToC(arc2x1), uToC(arc2y1), 
            uToC(arc2x2), uToC(arc2y2), 
            start=0, extent=-180, 
            fill="", outline=INACTIVE_COLOR, width=2, style="arc")

        l1x = self.centerX - r
        ly1 = (self.centerY - 1) + r 
        ly2 = (self.centerY + 1) - r
        l2x = self.centerX + r

        self.line1 = self.master.create_line(uToC(l1x) + 1, uToC(ly1), uToC(l1x) + 1, uToC(ly2) + 1, fill=INACTIVE_COLOR, width=2)
        self.line2 = self.master.create_line(uToC(l2x), uToC(ly1), uToC(l2x), uToC(ly2) + 1, fill=INACTIVE_COLOR, width=2)

        self.textObject = self.master.create_text(
            uToC(self.centerX),
            uToC(self.centerY),
            text=self.label,
            fill=INACTIVE_COLOR,
            font=FONT
        )

    def on(self):
        self.master.itemconfig(self.arc1, outline=ACTIVE_COLOR)
        self.master.itemconfig(self.arc2, outline=ACTIVE_COLOR)
        self.master.itemconfig(self.line1, fill=ACTIVE_COLOR)
        self.master.itemconfig(self.line2, fill=ACTIVE_COLOR)
        self.master.itemconfig(self.textObject, fill='#000000')

    def off(self):
        self.master.itemconfig(self.arc1, outline=INACTIVE_COLOR)
        self.master.itemconfig(self.arc2, outline=INACTIVE_COLOR)
        self.master.itemconfig(self.line1, fill=INACTIVE_COLOR)
        self.master.itemconfig(self.line2, fill=INACTIVE_COLOR)
        self.master.itemconfig(self.textObject, fill=INACTIVE_COLOR)
