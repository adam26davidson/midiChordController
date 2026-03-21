from models.appParameter import AppParameter

from .constants import ACTIVE_COLOR, FONT, INACTIVE_COLOR
from .controlButton import ControlButton


class DPadButton(ControlButton):

    radius = 2.5

    def __init__(self, master, param: AppParameter, type: str, direction, center_x, center_y):
        super().__init__(master)
        self.master = master

        self.center_x = center_x
        self.center_y = center_y
        self.direction = direction

        self.set_param(param, type, False)

        self.draw_button()

    def set_param(self, param: AppParameter, type: str, update: bool = True):
        self.param = param
        self.type = type
        if not param:
            self.label = "∅"
        else:
            if type == "POLAR":
                if self.direction == "LEFT" or self.direction == "DOWN":
                    self.label = f"-{param.label_abreviation}"
                else:
                    self.label = f"+{param.label_abreviation}"
            else:
                self.label = param.label_abreviation

        if update:
            self.master.itemconfig(self.text_object, text=self.label)

    def draw_button(self):
        c_x = self.center_x
        c_y = self.center_y

        if (self.direction == "LEFT"):
            xl1 = c_x - self.radius
            xl2 = xl1 + 1
            xl3 = xl2 + 1
            xlt = xl1 + 0.75
            self.draw_button_from_params(xl1, c_y+1, xl2, c_y+1, xl3, c_y, xl2, c_y-1, xl1, c_y-1, xlt, c_y)
        elif (self.direction == "RIGHT"):
            xr1 = c_x + self.radius
            xr2 = xr1 - 1
            xr3 = xr2 - 1
            xrt = xr1 - 0.75
            self.draw_button_from_params(xr1, c_y+1, xr2, c_y+1, xr3, c_y, xr2, c_y-1, xr1, c_y-1, xrt, c_y)
        elif (self.direction == "UP"):
            yt1 = c_y - self.radius
            yt2 = yt1 + 1
            yt3 = yt2 + 1
            ytt = yt1 + 0.75
            self.draw_button_from_params(c_x-1, yt1, c_x-1, yt2, c_x, yt3, c_x+1, yt2, c_x+1, yt1, c_x, ytt)
        elif (self.direction == "DOWN"):
            yb1 = c_y + self.radius
            yb2 = yb1 - 1
            yb3 = yb2 - 1
            ybt = yb1 - 0.75
            self.draw_button_from_params(c_x-1, yb1, c_x-1, yb2, c_x, yb3, c_x+1, yb2, c_x+1, yb1, c_x, ybt)

    def draw_button_from_params(self, x1, y1, x2, y2, x3, y3, x4, y4, x5, y5, tx, ty):
        u_to_c = self.master.units_to_coord
        self.canvas_object = self.master.create_polygon(
            u_to_c(x1), u_to_c(y1),
            u_to_c(x2), u_to_c(y2),
            u_to_c(x3), u_to_c(y3),
            u_to_c(x4), u_to_c(y4),
            u_to_c(x5), u_to_c(y5),
            fill="#000000",
            outline=INACTIVE_COLOR,
            width=2
        )
        self.text_object = self.master.create_text(
            u_to_c(tx),
            u_to_c(ty),
            text=self.label,
            fill=INACTIVE_COLOR,
            font=FONT
        )

    def on(self):
        self.master.itemconfig(self.canvas_object, outline=ACTIVE_COLOR, fill=ACTIVE_COLOR)
        self.master.itemconfig(self.text_object, fill='#000000')

    def off(self):
        self.master.itemconfig(self.canvas_object, outline=INACTIVE_COLOR, fill="#000000")
        self.master.itemconfig(self.text_object, fill=INACTIVE_COLOR)
