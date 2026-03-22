from __future__ import annotations

from typing import TYPE_CHECKING

from models.app_parameter import AppParameter

if TYPE_CHECKING:
    from .control_display import ControlDisplay

from .constants import ACTIVE_COLOR, FONT, INACTIVE_COLOR
from .control_button import ControlButton


class TriggerButton(ControlButton):

    width: int = 4
    height: float = 1.6
    radius: int = 1

    def __init__(self, master: ControlDisplay, param: AppParameter | None, center_x: float, center_y: float) -> None:
        super().__init__(master)
        self.master = master
        self.label: str = "∅" if not param else (param.label_abreviation or "")
        self.center_x = center_x
        self.center_y = center_y

        self.draw_button()

    def set_param(self, param: AppParameter | None) -> None:
        self.label = "∅" if not param else (param.label_abreviation or "")
        self.master.itemconfig(self.text_object, text=self.label)

    def draw_button(self) -> None:
        u_to_c = self.master.units_to_coord
        r = self.radius

        xl = self.center_x - (self.width / 2)
        xm1 = xl + r
        xm2 = (self.center_x + (self.width / 2)) - r
        xr = self.center_x + (self.width / 2)

        yt = self.center_y - (self.height / 2)
        ym = yt + r
        yb = self.center_y + (self.height / 2)

        self.arc1 = self.master.create_arc(
            u_to_c(xl) - 1, u_to_c(yt) - 1,
            u_to_c(xm1 + r), u_to_c(ym + r),
            start=180, extent=-90,
            fill="",
            outline=INACTIVE_COLOR,
            width=2,
            style="arc")

        self.arc2 = self.master.create_arc(
            u_to_c(xm2 - r), u_to_c(yt),
            u_to_c(xr), u_to_c(ym + r),
            start=0, extent=90,
            fill="",
            outline=INACTIVE_COLOR,
            width=2,
            style="arc")

        self.line1 = self.master.create_line(u_to_c(xm1) - 1, u_to_c(yt), u_to_c(xm2), u_to_c(yt), fill=INACTIVE_COLOR, width=2)
        self.line2 = self.master.create_line(u_to_c(xl), u_to_c(ym) - 1, u_to_c(xl), u_to_c(yb), fill=INACTIVE_COLOR, width=2)
        self.line3 = self.master.create_line(u_to_c(xl), u_to_c(yb), u_to_c(xr), u_to_c(yb), fill=INACTIVE_COLOR, width=2)
        self.line4 = self.master.create_line(u_to_c(xr), u_to_c(ym), u_to_c(xr), u_to_c(yb), fill=INACTIVE_COLOR, width=2)
        self.background1 = self.master.create_rectangle(
            u_to_c(xm1)+2, u_to_c(yt)+2, u_to_c(xm2)-1, u_to_c(yb)-2,
            fill="#000000",
            outline="#000000",
            width=2
        )
        self.background2 = self.master.create_rectangle(
            u_to_c(xl)+2, u_to_c(ym), u_to_c(xr)-2, u_to_c(yb)-2,
            fill="#000000",
            outline="#000000",
            width=2
        )

        self.text_object = self.master.create_text(
            u_to_c(self.center_x),
            u_to_c(self.center_y),
            text=self.label,
            fill=INACTIVE_COLOR,
            font=FONT
        )

    def on(self) -> None:
        self.master.itemconfig(self.arc1, outline=ACTIVE_COLOR, fill=ACTIVE_COLOR, style="pieslice")
        self.master.itemconfig(self.arc2, outline=ACTIVE_COLOR, fill=ACTIVE_COLOR, style="pieslice")
        self.master.itemconfig(self.background1, fill=ACTIVE_COLOR, outline=ACTIVE_COLOR)
        self.master.itemconfig(self.background2, fill=ACTIVE_COLOR, outline=ACTIVE_COLOR)
        self.master.itemconfig(self.line1, fill=ACTIVE_COLOR)
        self.master.itemconfig(self.line2, fill=ACTIVE_COLOR)
        self.master.itemconfig(self.line3, fill=ACTIVE_COLOR)
        self.master.itemconfig(self.line4, fill=ACTIVE_COLOR)
        self.master.itemconfig(self.text_object, fill='#000000')

    def off(self) -> None:
        self.master.itemconfig(self.arc1, outline=INACTIVE_COLOR, fill='#000000', style="arc")
        self.master.itemconfig(self.arc2, outline=INACTIVE_COLOR, fill='#000000', style="arc")
        self.master.itemconfig(self.background1, fill="#000000", outline="#000000")
        self.master.itemconfig(self.background2, fill="#000000", outline="#000000")
        self.master.itemconfig(self.line1, fill=INACTIVE_COLOR)
        self.master.itemconfig(self.line2, fill=INACTIVE_COLOR)
        self.master.itemconfig(self.line3, fill=INACTIVE_COLOR)
        self.master.itemconfig(self.line4, fill=INACTIVE_COLOR)
        self.master.itemconfig(self.text_object, fill=INACTIVE_COLOR)
