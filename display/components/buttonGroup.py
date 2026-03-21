import tkinter as tk

from ..displayConstants import COLORS, FONTS
from .settingControl import SettingControl


class ButtonGroup(SettingControl):

    def __init__(self, container, name, options_list, selected, callback):
        super().__init__(container, name)

        self.options_list = options_list
        self.callback = callback

        self.state = ButtonGroupState(selected)

        self.contents_frame = tk.Frame(self,
            highlightthickness=0,
            relief="flat",
            bg="#000000")

        self.buttons = {}

        for option in options_list:
            self.buttons[option['name']] = SingleButton(self.contents_frame, option, self.set_selected_button)
            self.buttons[option['name']].pack(side='left')

        self.buttons[selected].set_selected()

        self.contents_frame.pack(side='top', anchor='nw', padx=(4, 4), pady=(4, 4))

    def set_selected_button(self, value, name):
        self.buttons[self.state.active_button].set_un_selected()
        self.buttons[name].set_selected()
        self.state.active_button = name
        self.callback(value)

    def set_value(self, value):
        button = None
        for b in self.buttons.values():
            if b.value == value:
                button = b

        self.set_selected_button(value, button.name)

    def get_value(self):
        return self.buttons[self.state.active_button].value

    def set_disabled(self):
        for button_name in self.buttons:
            button = self.buttons[button_name]
            button.configure(state=tk.DISABLED)
            if button_name == self.state.active_button:
                button.configure(
                    bg=COLORS['chordDim'],
                    fg='#000000',
                    disabledforeground='#000000'
                )

    def set_enabled(self):
        for button_name in self.buttons:
            button = self.buttons[button_name]
            button.configure(state=tk.NORMAL)
            if button_name == self.state.active_button:
                button.configure(
                    bg=COLORS['root'],
                    fg='#000000'
                )


class SingleButton(tk.Button):

    def __init__(self, container, option, callback):
        self.value = option['value']
        self.name = option['name']
        self.callback = callback
        super().__init__(container,
            highlightthickness=0,
            relief="flat",
            height=3,
            width=5,
            bd=4,
            bg="#000000",
            activebackground="#000000",
            fg=COLORS['chordDim'],
            activeforeground=COLORS['chordDim'],
            disabledforeground='#000000',
            font=FONTS["medium"],
            text=option['name'],
            command=self.__on_click)

    def __on_click(self):
        self.callback(self.value, self.name)

    def set_selected(self):
        self.configure(
            bg=COLORS['root'],
            activebackground=COLORS['root'],
            fg="#000000",
            activeforeground="#000000")

    def set_un_selected(self):
        self.configure(
            bg="#000000",
            activebackground="#000000",
            fg=COLORS['chordDim'],
            activeforeground=COLORS['chordDim'])


class ButtonGroupState:
    disabled = False
    active_button = ''

    def __init__(self, active_button):
        self.active_button = active_button
