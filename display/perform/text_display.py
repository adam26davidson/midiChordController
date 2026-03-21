import tkinter as tk

from PIL import Image, ImageTk

from constants import PARENT_PATH

from ..display_constants import COLORS, FONTS


class TextDisplay(tk.Frame):
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

        FONTS["big"]
        FONTS["medium"]
        FONTS["small"]
        small_bold_font = FONTS["smallBold"]

        row_spacing = 50

        self.row_frame = tk.Frame(self, bg=self.bg_color)
        self.row_frame.pack(side="top")

        # octave
        self.octave_frame = tk.Frame(self.row_frame, bg=self.bg_color)
        self.octave_label = tk.Label(self.octave_frame, text="o: ", bg=self.bg_color, fg=self.inactive_color, font=small_bold_font)
        self.octave_value = tk.Label(self.octave_frame, text="0", bg=self.bg_color, fg=self.active_color, font=small_bold_font)
        self.octave_label.pack(side="left")
        self.octave_value.pack(side="left")
        self.octave_frame.pack(side="left", padx=(0, 0))

        # voices
        self.voices_frame = tk.Frame(self.row_frame, bg=self.bg_color)
        self.voices_label = tk.Label(self.voices_frame, text="v: ", bg=self.bg_color, fg=self.inactive_color, font=small_bold_font)
        self.voices_value = tk.Label(self.voices_frame, text="0", bg=self.bg_color, fg=self.active_color, font=small_bold_font)
        self.voices_label.pack(side="left")
        self.voices_value.pack(side="left")
        self.voices_frame.pack(side="left", padx=(row_spacing, 0))

        # lock and hold
        self.locked_image = Image.open(PARENT_PATH + "/display/images/padlock.png")
        self.locked_icon = ImageTk.PhotoImage(self.locked_image)

        self.unlocked_image = Image.open(PARENT_PATH + "/display/images/padlock-unlock.png")
        self.unlocked_icon = ImageTk.PhotoImage(self.unlocked_image)

        self.hold_active_image = Image.open(PARENT_PATH + "/display/images/hold-active.png")
        self.hold_active_icon = ImageTk.PhotoImage(self.hold_active_image)

        self.hold_inactive_image = Image.open(PARENT_PATH + "/display/images/hold-inactive.png")
        self.hold_inactive_icon = ImageTk.PhotoImage(self.hold_inactive_image)

        self.inversion_lock_icon = tk.Label(self.row_frame, image=self.unlocked_icon, bg=self.bg_color, padx=5)
        self.inversion_lock_icon.pack(side="left", padx=(row_spacing, 0))

        self.hold_icon = tk.Label(self.row_frame, image=self.hold_inactive_icon, bg=self.bg_color, padx=5)
        self.hold_icon.pack(side="left", padx=(row_spacing, 0))

        self.pack(side="top", padx=(20, 20), pady=(15, 0))


    def set_controller(self, text: str) -> None:
        pass

    def set_inversion_lock(self, active):
        if active:
            self.inversion_lock_icon.configure(image=self.locked_icon)
        else:
            self.inversion_lock_icon.configure(image=self.unlocked_icon)

    def set_hold(self, active):
        if active:
            self.hold_icon.configure(image=self.hold_active_icon)
        else:
            self.hold_icon.configure(image=self.hold_inactive_icon)

    def set_octave(self, octave):
        self.octave_value.configure(text=str(octave))

    def set_voices(self, voices):
        self.voices_value.configure(text=str(voices))
