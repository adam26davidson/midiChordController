import tkinter as tk
from constants import PARENT_PATH
from .displayConstants import FONTS, COLORS
from PIL import ImageTk, Image


class TextDisplay(tk.Frame):
    width = 300
    height = 350

    bgColor = "#000000"
    color = COLORS["chord"]
    inactiveColor = COLORS["chordDim"]
    activeColor = COLORS["root"]

    def __init__(self, master=None):
        super().__init__(master, width=self.width, height=self.height,
                         highlightthickness=0, relief="flat", bg=self.bgColor)
        self.master = master

        bigFont = FONTS["big"]
        mediumFont = FONTS["medium"]
        smallFont = FONTS["small"]

        # setting dsiplay
        self.settingFrame = tk.Frame(self, bg=self.bgColor, width=self.width)
        self.settingFrame.pack(side="top")
        tk.Label(self.settingFrame, text="Setting: ", fg=self.inactiveColor,
                 bg=self.bgColor, font=smallFont).pack(side="left")
        self.setting = tk.Label(
            self.settingFrame, text="Loading...", bg=self.bgColor, fg=self.color, font=bigFont)
        self.setting.pack(side="left")

        # controller dsiplay
        self.controllerImage = Image.open(
            PARENT_PATH+"/display/images/game-controller.png")
        self.controllerIcon = ImageTk.PhotoImage(self.controllerImage)
        self.controllerFrame = tk.Frame(self, bg=self.bgColor)
        self.controllerFrame.pack(side="left")
        tk.Label(self.controllerFrame, image=self.controllerIcon,
                 bg=self.bgColor).pack(side="left")
        self.controller = tk.Label(
            self.controllerFrame, text="Not Connected",
            bg=self.bgColor, fg=self.color, font=mediumFont)
        self.controller.pack(side="left", padx=(10, 0))

        # lock and hold
        self.lockFrame = tk.Frame(self, bg=self.bgColor)
        self.lockFrame.pack(side="left", pady=(10, 0))

        self.lockedImage = Image.open(
            PARENT_PATH + "/display/images/padlock.png")
        self.lockedIcon = ImageTk.PhotoImage(self.lockedImage)

        self.unlockedImage = Image.open(
            PARENT_PATH + "/display/images/padlock-unlock.png")
        self.unlockedIcon = ImageTk.PhotoImage(self.unlockedImage)

        self.holdActiveImage = Image.open(
            PARENT_PATH + "/display/images/hold-active.png")
        self.holdActiveIcon = ImageTk.PhotoImage(self.holdActiveImage)

        self.holdInactiveImage = Image.open(
            PARENT_PATH + "/display/images/hold-inactive.png")
        self.holdInactiveIcon = ImageTk.PhotoImage(self.holdInactiveImage)

        self.inversionLockFrame = tk.Frame(self.lockFrame, bg=self.bgColor)
        self.inversionLockIcon = tk.Label(
            self.inversionLockFrame, image=self.unlockedIcon,
            bg=self.bgColor, padx=5)
        self.inversionLockText = tk.Label(
            self.inversionLockFrame, text="inv lock",
            bg=self.bgColor, fg=self.inactiveColor, font=mediumFont)
        self.inversionLockIcon.pack(side="left")
        self.inversionLockText.pack(side="left")
        self.inversionLockFrame.pack(side='left')

        self.holdFrame = tk.Frame(self.lockFrame, bg=self.bgColor)
        self.holdIcon = tk.Label(
            self.holdFrame, image=self.holdInactiveIcon,
            bg=self.bgColor, padx=5)
        self.holdText = tk.Label(
            self.holdFrame, text="hold",
            bg=self.bgColor, fg=self.inactiveColor, font=mediumFont)
        self.holdIcon.pack(side="left")
        self.holdText.pack(side="left")
        self.holdFrame.pack(side='left', padx=(20, 0))

        self.octaveFrame = tk.Frame(self, bg=self.bgColor)
        self.octaveLabel = tk.Label(
            self.octaveFrame, text="octave: ",
            bg=self.bgColor, fg=self.color, font=mediumFont)
        self.octaveValue = tk.Label(
            self.octaveFrame, text="0",
            bg=self.bgColor, fg=self.activeColor, font=bigFont)
        self.octaveLabel.pack(side="left")
        self.octaveValue.pack(side="left")
        self.octaveFrame.pack(side='left', pady=(0, 0))

        self.voicesFrame = tk.Frame(self, bg=self.bgColor)
        self.voicesLabel = tk.Label(
            self.voicesFrame, text="voices: ",
            bg=self.bgColor, fg=self.color, font=mediumFont)
        self.voicesValue = tk.Label(
            self.voicesFrame, text="0",
            bg=self.bgColor, fg=self.activeColor, font=bigFont)
        self.voicesLabel.pack(side="left")
        self.voicesValue.pack(side="left")
        self.voicesFrame.pack(side='left', pady=(0, 0))

        self.pack(side="top", padx=(20, 20), pady=(20, 20))

    def setSetting(self, name):
        print('setting setting text to ' + name)
        self.setting.configure(text=name)

    def setController(self, name):
        self.controller.configure(text=name)

    def setInversionLock(self, active):
        if active:
            self.inversionLockText.configure(fg=self.activeColor)
            self.inversionLockIcon.configure(image=self.lockedIcon)
        else:
            self.inversionLockText.configure(fg=self.inactiveColor)
            self.inversionLockIcon.configure(image=self.unlockedIcon)

    def setHold(self, active):
        if active:
            self.holdText.configure(fg=self.activeColor)
            self.holdIcon.configure(image=self.holdActiveIcon)
        else:
            self.holdText.configure(fg=self.inactiveColor)
            self.holdIcon.configure(image=self.holdInactiveIcon)

    def setOctave(self, octave):
        self.octaveValue.configure(text=str(octave))

    def setVoices(self, voices):
        self.voicesValue.configure(text=str(voices))
