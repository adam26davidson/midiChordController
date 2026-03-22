from __future__ import annotations

from typing import TYPE_CHECKING

from models.app_parameter import AppParameter

if TYPE_CHECKING:
    from .control_display import ControlDisplay

from .constants import FONT, INACTIVE_COLOR
from .control_button import ControlButton


class TouchPadButton(ControlButton):

    width: int = 4
    height: int = 3

    def __init__(self, master: ControlDisplay, x_param: AppParameter | None, y_param: AppParameter | None, center_x: float, center_y: float) -> None:
        super().__init__(master)
        self.master = master
        self.x_label: str = "∅" if not x_param else (x_param.label_abreviation or "")
        self.y_label: str = "∅" if not y_param else (y_param.label_abreviation or "")
        self.center_x = center_x
        self.center_y = center_y

        self.draw_button()

    def set_x_param(self, param: AppParameter | None) -> None:
        self.x_label = "∅" if not param else (param.label_abreviation or "")
        self.master.itemconfig(self.x_text_object, text=f"x: {self.x_label}\ny: {self.y_label}")

    def set_y_param(self, param: AppParameter | None) -> None:
        self.y_label = "∅" if not param else (param.label_abreviation or "")
        self.master.itemconfig(self.x_text_object, text=f"x: {self.x_label}\ny: {self.y_label}")

    def draw_button(self) -> None:
        u_to_c = self.master.units_to_coord
        xl = self.center_x - (self.width / 2)
        xr = self.center_x + (self.width / 2)
        yt = self.center_y - (self.height / 2)
        yb = self.center_y + (self.height / 2)

        self.canvas_object = self.master.create_rectangle(
            u_to_c(xl), u_to_c(yt), u_to_c(xr), u_to_c(yb),
            fill="#000000",
            outline=INACTIVE_COLOR,
            width=2
        )

        self.x_text_object = self.master.create_text(
            u_to_c(self.center_x),
            u_to_c(self.center_y),
            text=f"x: {self.x_label}\ny: {self.y_label}",
            fill=INACTIVE_COLOR,
            font=FONT
        )

    def update_x(self, value: float) -> None:
        pass

    def update_y(self, value: float) -> None:
        pass
