from models.appParameter import AppParameter

from .constants import ACTIVE_COLOR, FONT, INACTIVE_COLOR
from .controlButton import ControlButton


class BumperButton(ControlButton):

    width = 4
    height = 1.6

    def __init__(self, master, param: AppParameter, center_x, center_y):
        super().__init__(master)
        self.master = master
        self.label = "∅" if not param else param.label_abreviation
        self.center_x = center_x
        self.center_y = center_y

        self.draw_button()

    def set_param(self, param: AppParameter):
        self.label = "∅" if not param else param.label_abreviation
        self.master.itemconfig(self.text_object, text=self.label)

    def draw_button(self):
        u_to_c = self.master.units_to_coord
        self.canvas_object = self.master.create_rectangle(
            u_to_c(self.center_x - (self.width / 2)),
            u_to_c(self.center_y - (self.height / 2)),
            u_to_c(self.center_x + (self.width / 2)),
            u_to_c(self.center_y + (self.height / 2)),
            fill="#000000",
            outline=INACTIVE_COLOR,
            width=2
        )

        self.text_object = self.master.create_text(
            u_to_c(self.center_x),
            u_to_c(self.center_y),
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
