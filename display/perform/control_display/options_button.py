from models.app_parameter import AppParameter

from .constants import ACTIVE_COLOR, FONT, INACTIVE_COLOR
from .control_button import ControlButton


class OptionsButton(ControlButton):

    x_offset = 0.2
    y_offset = 0.2
    line_extension = 0.05

    def __init__(self, master, param: AppParameter, center_x, center_y, unit_size):
        super().__init__(master)
        self.master = master
        self.label = "∅" if not param else param.label_abreviation

        self.center_x = center_x
        self.center_y = center_y
        self.unit_size = unit_size
        self.radius = unit_size

        self.draw_button()

    def set_param(self, param: AppParameter):
        self.label = "∅" if not param else param.label_abreviation
        self.master.itemconfig(self.text_object, text=self.label)

    def draw_button(self):
        u_to_c = self.master.units_to_coord
        r = (1 - self.x_offset)
        arc1x1 = self.center_x - r
        arc1y1 = self.center_y - 1
        arc1x2 = self.center_x + r
        arc1y2 = arc1y1 + (2*r)
        self.arc1 = self.master.create_arc(
            u_to_c(arc1x1), u_to_c(arc1y1),
            u_to_c(arc1x2), u_to_c(arc1y2),
            start=0, extent=180,
            fill="",
            outline=INACTIVE_COLOR,
            width=2,
            style="arc")

        arc2x1 = self.center_x - r
        arc2y1 = (self.center_y + 1) - (2*r)
        arc2x2 = self.center_x + r
        arc2y2 = arc2y1 + (2*r)
        self.arc2 = self.master.create_arc(
            u_to_c(arc2x1), u_to_c(arc2y1),
            u_to_c(arc2x2), u_to_c(arc2y2),
            start=0, extent=-180,
            fill="", outline=INACTIVE_COLOR, width=2, style="arc")

        l1x = self.center_x - r
        ly1 = (self.center_y - 1) + r
        ly2 = (self.center_y + 1) - r
        l2x = self.center_x + r

        self.line1 = self.master.create_line(u_to_c(l1x) + 1, u_to_c(ly1), u_to_c(l1x) + 1, u_to_c(ly2) + 1, fill=INACTIVE_COLOR, width=2)
        self.line2 = self.master.create_line(u_to_c(l2x), u_to_c(ly1), u_to_c(l2x), u_to_c(ly2) + 1, fill=INACTIVE_COLOR, width=2)

        self.background = self.master.create_rectangle(
            u_to_c(l1x)+2,
            u_to_c(ly1),
            u_to_c(l2x)-2,
            u_to_c(ly2),
            fill="#000000",
            outline="#000000"
        )

        self.text_object = self.master.create_text(
            u_to_c(self.center_x),
            u_to_c(self.center_y),
            text=self.label,
            fill=INACTIVE_COLOR,
            font=FONT
        )

    def on(self):
        self.master.itemconfig(self.arc1, outline=ACTIVE_COLOR, fill=ACTIVE_COLOR, style="pieslice")
        self.master.itemconfig(self.arc2, outline=ACTIVE_COLOR, fill=ACTIVE_COLOR, style="pieslice")
        self.master.itemconfig(self.background, fill=ACTIVE_COLOR, outline=ACTIVE_COLOR)
        self.master.itemconfig(self.line1, fill=ACTIVE_COLOR)
        self.master.itemconfig(self.line2, fill=ACTIVE_COLOR)
        self.master.itemconfig(self.text_object, fill='#000000')

    def off(self):
        self.master.itemconfig(self.arc1, outline=INACTIVE_COLOR, fill=INACTIVE_COLOR, style="arc")
        self.master.itemconfig(self.arc2, outline=INACTIVE_COLOR, fill=INACTIVE_COLOR, style="arc")
        self.master.itemconfig(self.background, fill="#000000", outline="#000000")
        self.master.itemconfig(self.line1, fill=INACTIVE_COLOR)
        self.master.itemconfig(self.line2, fill=INACTIVE_COLOR)
        self.master.itemconfig(self.text_object, fill=INACTIVE_COLOR)
