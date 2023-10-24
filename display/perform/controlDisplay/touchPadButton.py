from models.appParameter import AppParameter
from .controlButton import ControlButton
from .constants import ACTIVE_COLOR, INACTIVE_COLOR, FONT


class TouchPadButton(ControlButton):

    width = 4
    height = 3

    def __init__(self, master, xParam: AppParameter, yParam: AppParameter, centerX, centerY):
        super().__init__(master)
        self.master = master
        self.xLabel = "∅" if not xParam else xParam.labelAbreviation
        self.yLabel = "∅" if not yParam else yParam.labelAbreviation
        self.centerX = centerX
        self.centerY = centerY

        self.drawButton()

    def setXParam(self, param: AppParameter):
        self.xLabel = "∅" if not param else param.labelAbreviation
        self.master.itemconfig(self.xTextObject, text=f"x: {self.xLabel}\ny: {self.yLabel}")

    def setYParam(self, param: AppParameter):
        self.yLabel = "∅" if not param else param.labelAbreviation
        self.master.itemconfig(self.xTextObject, text=f"x: {self.xLabel}\ny: {self.yLabel}")

    def drawButton(self):
        uToC = self.master.unitsToCoord
        xl = self.centerX - (self.width / 2)
        xr = self.centerX + (self.width / 2)
        yt = self.centerY - (self.height / 2)
        yb = self.centerY + (self.height / 2)

        self.canvasObject = self.master.create_rectangle(
            uToC(xl), uToC(yt), uToC(xr), uToC(yb),
            fill="#000000",
            outline=INACTIVE_COLOR,
            width=2
        )

        self.xTextObject = self.master.create_text(
            uToC(self.centerX),
            uToC(self.centerY),
            text=f"x: {self.xLabel}\ny: {self.yLabel}",
            fill=INACTIVE_COLOR,
            font=FONT
        )

    def update_x(self, value):
        pass

    def update_y(self, value):
        pass
    