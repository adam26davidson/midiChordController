from __future__ import annotations

from typing import TYPE_CHECKING

from models.app_parameter import AppParameter

if TYPE_CHECKING:
    from .control_display import ControlDisplay

from .constants import ACTIVE_COLOR, FONT, INACTIVE_COLOR
from .control_button import ControlButton


class CircularButton(ControlButton):

    def __init__(self, master: ControlDisplay, param: AppParameter | None, center_x: float, center_y: float, unit_size: float) -> None:
        super().__init__(master)
        self.master = master
        self.label: str = "∅" if not param else (param.label_abreviation or "")
        self.center_x = center_x
        self.center_y = center_y
        self.unit_size = unit_size
        self.radius = unit_size

        self.draw_button()

    def set_param(self, param: AppParameter | None) -> None:
        self.label = "∅" if not param else (param.label_abreviation or "")
        self.master.itemconfig(self.text_object, text=self.label)

    def draw_button(self) -> None:
        self.canvas_object = self.master.create_oval(
            self.center_x - self.radius,
            self.center_y - self.radius,
            self.center_x + self.radius,
            self.center_y + self.radius,
            fill="#000000",
            outline=INACTIVE_COLOR,
            width=2
        )

        self.text_object = self.master.create_text(
            self.center_x,
            self.center_y,
            text=self.label,
            fill=INACTIVE_COLOR,
            font=FONT
        )

    def on(self) -> None:
        self.master.itemconfig(self.canvas_object, outline=ACTIVE_COLOR, fill=ACTIVE_COLOR)
        self.master.itemconfig(self.text_object, fill='#000000')

    def off(self) -> None:
        self.master.itemconfig(self.canvas_object, outline=INACTIVE_COLOR, fill="#000000")
        self.master.itemconfig(self.text_object, fill=INACTIVE_COLOR)
