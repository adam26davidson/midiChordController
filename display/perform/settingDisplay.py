import tkinter as tk
from constants import PARENT_PATH
from ..displayConstants import FONTS, COLORS
from PIL import ImageTk, Image


class SettingDisplay(tk.Frame):
    width = 300
    height = 50

    bgColor = "#000000"
    color = COLORS["chord"]
    inactiveColor = COLORS["chordDim"]
    activeColor = COLORS["root"]

    def __init__(self, master=None):
        super().__init__(master, width=self.width, height=self.height,
                         highlightthickness=0, relief="flat", bg=self.bgColor, border=2, borderwidth=2)
        self.master = master

        bigFont = FONTS["big"]
        smallFont = FONTS["small"]

        # setting dsiplay
        self.settingFrame = tk.Frame(self, bg=self.bgColor, width=self.width)
        self.settingFrame.pack(side="top", anchor="nw")
        tk.Label(self.settingFrame, text="Setting: ", fg=self.inactiveColor, bg=self.bgColor, font=smallFont).pack(side="left")
        self.setting = tk.Label(self.settingFrame, text="Loading...", bg=self.bgColor, fg=self.color, font=bigFont)
        self.setting.pack(side="top", pady=(0, 0))

        self.pack(side="top", anchor="nw", padx=(20, 20), pady=20)


    def setSetting(self, name):
        print('setting setting text to ' + name)
        self.setting.configure(text=name)

