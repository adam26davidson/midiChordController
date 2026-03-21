
from models.app_parameter import AppParameter

from .constants import ACTIVE_COLOR, FONT, INACTIVE_COLOR
from .control_button import ControlButton


class JoyStickButton(ControlButton):

    radius = 1.4
    text_radius = 0.7

    def __init__(self, master,
                 x_params: list[AppParameter],
                 y_params: list[AppParameter],
                 x_type: str,
                 y_type: str,
                 c_param: AppParameter,
                 center_x, center_y, side):
        super().__init__(master)
        self.master = master

        self.set_x_params(x_params, x_type, False)
        self.set_y_params(y_params, y_type, False)

        self.click_label = "∅" if not c_param else c_param.label_abreviation
        self.center_x = center_x
        self.center_y = center_y
        self.side = side

        self.draw_button()

    def set_x_params(self, params: list[AppParameter], type: str, update: bool = True):
        self.set_axis_params(params, type, "X", update)

    def set_y_params(self, params: list[AppParameter], type: str, update: bool = True):
        self.set_axis_params(params, type, "Y", update)

    def set_axis_params(self, params: list[AppParameter], type: str, axis: str, update: bool = True):
        if axis == "X":
            self.x_params = params
            self.x_type = type
        else:
            self.y_params = params
            self.y_type = type

        if (len(params) == 0):
            if axis == "X":
                self.left_label = "∅"
                self.right_label = "∅"
            else:
                self.top_label = "∅"
                self.bottom_label = "∅"
        else:
            if type == "ANALOG" or type == "POLAR":
                if axis == "X":
                    self.left_label = f"-{params[0].label_abreviation}"
                    self.right_label = f"+{params[0].label_abreviation}"
                else:
                    self.top_label = f"+{params[0].label_abreviation}"
                    self.bottom_label = f"-{params[0].label_abreviation}"
            else:
                if axis == "X":
                    self.left_label = params[0].label_abreviation
                    self.right_label = params[1].label_abreviation
                else:
                    self.top_label = params[0].label_abreviation
                    self.bottom_label = params[1].label_abreviation

        if update:
            if axis == "X":
                self.master.itemconfig(self.left_text_object, text=self.left_label)
                self.master.itemconfig(self.right_text_object, text=self.right_label)
            else:
                self.master.itemconfig(self.top_text_object, text=self.top_label)
                self.master.itemconfig(self.bottom_text_object, text=self.bottom_label)


    def draw_button(self):
        u_to_c = self.master.units_to_coord
        r = self.radius
        cx = self.center_x
        cy = self.center_y

        self.canvas_object = self.master.create_oval(
            u_to_c(self.center_x - self.radius),
            u_to_c(self.center_y - self.radius),
            u_to_c(self.center_x + self.radius),
            u_to_c(self.center_y + self.radius),
            fill="#000000",
            outline=INACTIVE_COLOR,
            width=2
        )

        self.right_text_background_object , self.right_text_object = self.draw_text_and_background(self.right_label, cx + r, cy)
        self.left_text_background_object , self.left_text_object = self.draw_text_and_background(self.left_label, cx - r, cy)
        self.top_text_background_object , self.top_text_object = self.draw_text_and_background(self.top_label, cx, cy - r)
        self.bottom_text_background_object , self.bottom_text_object = self.draw_text_and_background(self.bottom_label, cx, cy + r)

        yl = cy + r
        if self.side == "LEFT":
            self.arrow_object = self.draw_text_for_click("↓", cx - (r + 0.5), yl)
            self.click_text_object = self.draw_text_for_click(self.click_label, cx - (r + 1.2), yl)
        else:
            self.arrow_object = self.draw_text_for_click("↓", cx + (r + 0.5), yl)
            self.click_text_object = self.draw_text_for_click(self.click_label, cx + (r + 1.2), yl)


    def draw_text_and_background(self, label, center_x, center_y):
        u_to_c = self.master.units_to_coord
        background_object = self.master.create_oval(
            u_to_c(center_x - self.text_radius),
            u_to_c(center_y - self.text_radius),
            u_to_c(center_x + self.text_radius),
            u_to_c(center_y + self.text_radius),
            fill="#000000",
            outline="#000000",
            width=2
        )

        text_object = self.master.create_text(
            u_to_c(center_x),
            u_to_c(center_y),
            text=label,
            fill=INACTIVE_COLOR,
            font=FONT
        )

        return background_object, text_object

    def draw_text_for_click(self, label, center_x, center_y):
        u_to_c = self.master.units_to_coord
        return self.master.create_text(
            u_to_c(center_x),
            u_to_c(center_y),
            text=label,
            fill=INACTIVE_COLOR,
            font=FONT
        )

    def button_on(self):
        self.master.itemconfig(self.arrow_object, fill=ACTIVE_COLOR)
        self.master.itemconfig(self.click_text_object, fill=ACTIVE_COLOR)

    def button_off(self):
        self.master.itemconfig(self.arrow_object, fill=INACTIVE_COLOR)
        self.master.itemconfig(self.click_text_object, fill=INACTIVE_COLOR)

    def left_on(self):
        self.master.itemconfig(self.left_text_background_object, fill=ACTIVE_COLOR, outline=ACTIVE_COLOR)
        self.master.itemconfig(self.left_text_object, fill="#000000")

    def left_off(self):
        self.master.itemconfig(self.left_text_background_object, fill="#000000", outline="#000000")
        self.master.itemconfig(self.left_text_object, fill=INACTIVE_COLOR)

    def right_on(self):
        self.master.itemconfig(self.right_text_background_object, fill=ACTIVE_COLOR, outline=ACTIVE_COLOR)
        self.master.itemconfig(self.right_text_object, fill="#000000")

    def right_off(self):
        self.master.itemconfig(self.right_text_background_object, fill="#000000", outline="#000000")
        self.master.itemconfig(self.right_text_object, fill=INACTIVE_COLOR)

    def up_on(self):
        self.master.itemconfig(self.top_text_background_object, fill=ACTIVE_COLOR, outline=ACTIVE_COLOR)
        self.master.itemconfig(self.top_text_object, fill="#000000")

    def up_off(self):
        self.master.itemconfig(self.top_text_background_object, fill="#000000", outline="#000000")
        self.master.itemconfig(self.top_text_object, fill=INACTIVE_COLOR)

    def down_on(self):
        self.master.itemconfig(self.bottom_text_background_object, fill=ACTIVE_COLOR, outline=ACTIVE_COLOR)
        self.master.itemconfig(self.bottom_text_object, fill="#000000")

    def down_off(self):
        self.master.itemconfig(self.bottom_text_background_object, fill="#000000", outline="#000000")
        self.master.itemconfig(self.bottom_text_object, fill=INACTIVE_COLOR)

    def update_x(self, value):
        pass

    def update_y(self, value):
        pass

