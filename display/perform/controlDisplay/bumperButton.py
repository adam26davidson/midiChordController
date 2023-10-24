from models.appParameter import AppParameter
from .controlButton import ControlButton
from .constants import ACTIVE_COLOR, INACTIVE_COLOR, FONT


class BumperButton(ControlButton):

    width = 4
    height = 1.75

    def __init__(self, master, param: AppParameter, centerX, centerY):
        super().__init__(master)
        self.master = master
        self.label = "∅" if not param else param.labelAbreviation
        self.centerX = centerX
        self.centerY = centerY

        self.drawButton()

    def setParam(self, param: AppParameter):
        self.label = param.labelAbreviation
        self.master.itemconfig(self.textObject, text=self.label)

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
            uToC(self.centerX),
            uToC(self.centerY),
            text=self.label,
            fill=INACTIVE_COLOR,
            font=FONT
        )
    
    def on(self):
        self.master.itemconfig(self.canvasObject, outline=ACTIVE_COLOR, fill=ACTIVE_COLOR)
        self.master.itemconfig(self.textObject, fill='#000000')

    def off(self):
        self.master.itemconfig(self.canvasObject, outline=INACTIVE_COLOR, fill="#000000")
        self.master.itemconfig(self.textObject, fill=INACTIVE_COLOR)