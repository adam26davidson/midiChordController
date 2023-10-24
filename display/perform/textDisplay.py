import tkinter as tk
from constants import PARENT_PATH
from ..displayConstants import FONTS, COLORS
from PIL import ImageTk, Image


class TextDisplay(tk.Frame):
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
        mediumFont = FONTS["medium"]
        smallFont = FONTS["small"]
        smallBoldFont = FONTS["smallBold"]

        rowSpacing = 40

        # octave
        self.octaveFrame = tk.Frame(self.rowFrame, bg=self.bgColor)
        self.octaveLabel = tk.Label(self.octaveFrame, text="o: ", bg=self.bgColor, fg=self.inactiveColor, font=smallBoldFont)
        self.octaveValue = tk.Label(self.octaveFrame, text="0", bg=self.bgColor, fg=self.activeColor, font=smallBoldFont)
        self.octaveLabel.pack(side="left")
        self.octaveValue.pack(side="left")
        self.octaveFrame.pack(side="left", padx=(rowSpacing, 0))

        # voices
        self.voicesFrame = tk.Frame(self.rowFrame, bg=self.bgColor)
        self.voicesLabel = tk.Label(self.voicesFrame, text="v: ", bg=self.bgColor, fg=self.inactiveColor, font=smallBoldFont)
        self.voicesValue = tk.Label(self.voicesFrame, text="0", bg=self.bgColor, fg=self.activeColor, font=smallBoldFont)
        self.voicesLabel.pack(side="left")
        self.voicesValue.pack(side="left")
        self.voicesFrame.pack(side="left", padx=(rowSpacing, 0))

        # lock and hold
        self.lockedImage = Image.open(PARENT_PATH + "/display/images/padlock.png")
        self.lockedIcon = ImageTk.PhotoImage(self.lockedImage)

        self.unlockedImage = Image.open(PARENT_PATH + "/display/images/padlock-unlock.png")
        self.unlockedIcon = ImageTk.PhotoImage(self.unlockedImage)

        self.holdActiveImage = Image.open(PARENT_PATH + "/display/images/hold-active.png")
        self.holdActiveIcon = ImageTk.PhotoImage(self.holdActiveImage)

        self.holdInactiveImage = Image.open(PARENT_PATH + "/display/images/hold-inactive.png")
        self.holdInactiveIcon = ImageTk.PhotoImage(self.holdInactiveImage)

        self.inversionLockIcon = tk.Label(self.rowFrame, image=self.unlockedIcon, bg=self.bgColor, padx=5)
        self.inversionLockIcon.pack(side="left", padx=(rowSpacing, 0))

        self.holdIcon = tk.Label(self.rowFrame, image=self.holdInactiveIcon, bg=self.bgColor, padx=5)
        self.holdIcon.pack(side="left", padx=(rowSpacing, 0))

        self.pack(side="top", anchor="nw", padx=(20, 20), pady=(0, 0))


    def setController(self, name):
        self.controller.configure(text=name)

    def setInversionLock(self, active):
        if active:
            self.inversionLockIcon.configure(image=self.lockedIcon)
        else:
            self.inversionLockIcon.configure(image=self.unlockedIcon)

    def setHold(self, active):
        if active:
            self.holdIcon.configure(image=self.holdActiveIcon)
        else:
            self.holdIcon.configure(image=self.holdInactiveIcon)

    def setOctave(self, octave):
        self.octaveValue.configure(text=str(octave))

    def setVoices(self, voices):
        self.voicesValue.configure(text=str(voices))
