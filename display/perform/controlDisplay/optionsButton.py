from .controlButton import ControlButton
from .constants import ACTIVE_COLOR, INACTIVE_COLOR, FONT


class OptionsButton(ControlButton):

    xOffset = 0.2
    yOffset = 0.2

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
        r = (1 - self.xOffset)
        arc1x1 = self.centerX - r
        arc1y1 = self.centerY - 1
        arc1x2 = self.centerX + r
        arc1y2 = arc1y1 + (2*r)
        self.arc1 = self.master.create_arc(arc1x1, arc1y1, arc1x2, arc1y2, start=0, extent=180, fill="", outline=INACTIVE_COLOR, width=2)
        
        arc2x1 = self.centerX - r
        arc2y1 = (self.centerY + 1) - (2*r)
        arc2x2 = self.centerX + r
        arc2y2 = arc2y1 + (2*r)
        self.arc2 = self.master.create_arc(arc2x1, arc2y1, arc2x2, arc2y2, start=180, extent=0, fill="", outline=INACTIVE_COLOR, width=2)

        l1x = self.centerX - r
        ly1 = (self.centerY - 1) + r
        ly2 = (self.centerY + 1) - r
        l2x = self.centerX + r

        self.line1 = self.master.create_line(l1x, ly1, l1x, ly2, fill=INACTIVE_COLOR, width=2)
        self.line2 = self.master.create_line(l2x, ly1, l2x, ly2, fill=INACTIVE_COLOR, width=2)

        self.textObject = self.master.create_text(
            self.centerX,
            self.centerY,
            text=self.label,
            fill="#ffffff",
            font=FONT
        )