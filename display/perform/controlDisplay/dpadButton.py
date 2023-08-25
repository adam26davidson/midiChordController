from .controlButton import ControlButton
from .constants import ACTIVE_COLOR, INACTIVE_COLOR, FONT

class DPadButton(ControlButton):

    def __init__(self, master, label, direction, unitSize):
        super().__init__(master, label)
        self.master = master
        self.label = label
        self.direction = direction
        self.unitSize = unitSize
        self.radius = unitSize

        self.drawButton()

    def drawButton(self):
        cX = self.unitSize * 3
        cY = self.unitSize * 9
        u = self.unitSize
        if (self.direction == "LEFT"):
            self.canvasObject = self.master.create_polygon(
                cX - 3*u, cY + u,
                cX - 2*u, cY + u,
                cX - u, cY,
                cX - 2*u, cY - u,
                cX - 3*u, cY - u,
                fill="#000000",
                outline=INACTIVE_COLOR,
                width=2
            )
            self.textObject = self.master.create_text(
                0.75*u,
                9*u,
                text=self.label,
                fill="#ffffff",
                font=FONT
            )
        elif (self.direction == "RIGHT"):
            self.canvasObject = self.master.create_polygon(
                cX + 3*u, cY + u,
                cX + 2*u, cY + u,
                cX + u, cY,
                cX + 2*u, cY - u,
                cX + 3*u, cY - u,
                fill="#000000",
                outline=INACTIVE_COLOR,
                width=2
            )
            self.textObject = self.master.create_text(
                5.25*u,
                9*u,
                text=self.label,
                fill="#ffffff",
                font=FONT
            )
        elif (self.direction == "UP"):
            self.canvasObject = self.master.create_polygon(
                cX - u, cY - 3*u,
                cX - u, cY - 2*u,
                cX, cY - u,
                cX + u, cY - 2*u,
                cX + u, cY - 3*u,
                fill="#000000",
                outline=INACTIVE_COLOR,
                width=2
            )
            self.textObject = self.master.create_text(
                3*u,
                6.75*u,
                text=self.label,
                fill="#ffffff",
                font=FONT
            )
        elif (self.direction == "DOWN"):
            self.canvasObject = self.master.create_polygon(
                cX - u, cY + 3*u,
                cX - u, cY + 2*u,
                cX, cY + u,
                cX + u, cY + 2*u,
                cX + u, cY + 3*u,
                fill="#000000",
                outline=INACTIVE_COLOR,
                width=2
            )
            self.textObject = self.master.create_text(
                3*u,
                11.25*u,
                text=self.label,
                fill="#ffffff",
                font=FONT
            )

    