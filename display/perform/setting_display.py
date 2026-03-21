import tkinter as tk

from pyrsistent import thaw

from redux import store

from ..display_constants import COLORS, FONTS


class SettingDisplay(tk.Frame):
    width = 300
    height = 50

    bg_color = "#000000"
    color = COLORS["chord"]
    inactive_color = COLORS["chordDim"]
    active_color = COLORS["root"]

    def __init__(self, master=None):
        super().__init__(master, width=self.width, height=self.height,
                         highlightthickness=0, relief="flat", bg=self.bg_color, border=2, borderwidth=2)
        self.parent = master
        self.chord_engine_control = 'internal'
        self.internal_setting_name = 'Loading...'

        big_font = FONTS["big"]
        small_font = FONTS["small"]

        # setting dsiplay
        self.setting_frame = tk.Frame(self, bg=self.bg_color, width=self.width)
        self.setting_frame.pack(side="top", anchor="nw")
        tk.Label(self.setting_frame, text="Setting: ", fg=self.inactive_color, bg=self.bg_color, font=small_font).pack(side="left")
        self.setting = tk.Label(self.setting_frame, text="Loading...", bg=self.bg_color, fg=self.color, font=big_font)
        self.setting.pack(side="top", pady=(0, 0))

        self.pack(side="top", anchor="nw", padx=(20, 20), pady=20)

        store.subscribe(self.__handle_store_update)

    def __handle_store_update(self):
        state = thaw(store.get_state()['musicEngine'])
        if state['chordEngineControl'] != self.chord_engine_control:
            self.chord_engine_control = state['chordEngineControl']
            self.set_chord_engine_control(state['chordEngineControl'])

    def set_chord_engine_control(self, name):
        if name == 'internal':
            self.set_setting(self.internal_setting_name)
        else:
            self.set_setting("External Control")

    def set_setting(self, name):
        if self.chord_engine_control == 'internal':
            self.internal_setting_name = name
        print('setting setting text to ' + name)
        self.setting.configure(text=name)

