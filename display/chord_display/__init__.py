from __future__ import annotations

import math
import time
import tkinter as tk
from typing import Any

from constants import *  # noqa: F403

from ..display_constants import COLORS, FONTS
from .chord_name import ChordName


class ChordDisplay(tk.Canvas):
    height = 340
    radius = 110
    x_margin = 20

    small_note_radius = 16
    large_note_radius = 18
    outline_width = 4

    bass_note_shadow_radius = 21
    bass_note_played_radius = 23
    bass_dash = ()
    bass_outline_shadow_width = 6
    bass_outline_played_width = 10

    mod_animation_length = 0.15

    key_text_offset = -50
    key_text_font_size = 30

    note_names = [
        "C",
        "C#/Db",
        "D",
        "D#/Eb",
        "E",
        "F",
        "F#/Gb",
        "G",
        "G#/Ab",
        "A",
        "A#/Bb",
        "B",
    ]

    def __init__(self, master=None):
        self.width = (self.radius + self.bass_note_played_radius + self.x_margin) * 2
        super().__init__(
            master,
            width=self.width,
            height=self.height,
            highlightthickness=0,
            relief="flat",
            bg="#222222",
        )
        self.scale_notes: list[int] = [0, 2, 4, 5, 7, 9, 11]
        self.modulation_state: dict[str, Any] = {
            "side": "none",
            "oldScale": [0, 2, 4, 5, 7, 9, 11],
            "newScale": None,
            "status": "none",
            "startTime": 0,
        }
        self.animation_in_progress = False
        self.parent = master
        self.key = 0
        self.root = 0
        self.bass_note = 0
        self.chord: list[Any] = []
        self.notes = self.create_notes()
        self.key_text = self.create_key_text()
        self.chord_name = ChordName(self)
        self.bass = self.create_bass_note()
        # self.bassPlayed = self.createBassPlayedNote()
        self.pack(side="top", pady=(20, 0), padx=(0, 0))

    def create_key_text(self):
        x = self.width / 2
        y = self.notes[0]["center"]["y"] + self.key_text_offset
        return self.create_text(
            x, y, fill=COLORS["chord"], text=self.note_names[self.key], font=FONTS["big"]
        )

    def create_bass_note(self):
        center = self.notes[0]["center"]
        r = self.bass_note_shadow_radius
        x0, x1 = center["x"] - r, center["x"] + r
        y0, y1 = center["y"] - r, center["y"] + r
        bass_note = self.create_oval(
            x0,
            y0,
            x1,
            y1,
            fill="",
            outline=COLORS["root"],
            dash=self.bass_dash,
            width=self.bass_outline_shadow_width,
        )
        return {"id": bass_note, "note": 0, "radius": r}

    def create_notes(self):
        notes = []
        center_x = self.width / 2
        center_y = (self.height - (0.5*self.key_text_offset)) / 2
        for i in range(12):
            color = ""
            if self.scale_notes.count(i) != 0:
                color = COLORS["chordDim"]
            theta = ((i * -2 * math.pi) / 12) + (0.5 * math.pi)
            x = center_x + (self.radius * math.cos(theta))
            y = center_y - (self.radius * math.sin(theta))
            x0, x1 = x - self.small_note_radius, x + self.small_note_radius
            y0, y1 = y - self.small_note_radius, y + self.small_note_radius

            note = {
                "id": self.create_oval(
                    x0, y0, x1, y1, width=self.outline_width, fill="", outline=color
                ),
                "center": {"x": x, "y": y},
                "radius": self.small_note_radius,
            }
            notes.append(note)
        return notes

    def set_note_position(self, note, x, y):
        r = self.notes[note]["radius"]
        x0, x1 = x - r, x + r
        y0, y1 = y - r, y + r
        self.coords(self.notes[note]["id"], x0, y0, x1, y1)

    def run_animation_step(self):
        if self.modulation_state["status"] == "startAnimation":
            t = time.time() - self.modulation_state["startTime"]
            for note in self.modulation_state["newScale"]:
                center = self.get_note_position(note)
                self.set_note_position(note, center["x"], center["y"])
            self.set_bass_position_and_radius(self.bass["note"], self.bass["radius"])
            if t > self.mod_animation_length:
                self.modulation_state["status"] = "active"

    def distance(self, x0, y0, x1, y1):
        return math.sqrt(((x1 - x0) ** 2) + ((y0 - y1) ** 2))

    def calculate_animated_note_distance(self, d_total, t):
        if d_total == 0:
            return 0
        t_max = self.mod_animation_length
        if t <= t_max / 2:
            return ((2 * d_total) / (t_max**2)) * (t**2)
        if t > t_max / 2 and t <= t_max:
            return ((((-2 * d_total) / (t_max**2)) * (t**2)) + ((4 * d_total * t) / t_max)) - d_total
        return d_total

    def get_note_position(self, note):
        if self.modulation_state["status"] == "none":
            return self.notes[note]["center"]
        if self.modulation_state["status"] == "startAnimation":
            new_scale = self.modulation_state["newScale"]
            old_scale = self.modulation_state["oldScale"]
            if note in new_scale:
                t = time.time() - self.modulation_state["startTime"]
                index = new_scale.index(note)
                old_note = old_scale[index]
                center0 = self.notes[old_note]["center"]
                center1 = self.notes[note]["center"]
                x0, y0 = center0["x"], center0["y"]
                x1, y1 = center1["x"], center1["y"]
                d_total = self.distance(x0, y0, x1, y1)
                if d_total != 0:
                    d = self.calculate_animated_note_distance(d_total, t)
                    x = x0 + (((x1 - x0) * d) / d_total)
                    y = y0 + (((y1 - y0) * d) / d_total)
                    return {"x": x, "y": y}
                return self.notes[note]["center"]
            return self.notes[note]["center"]
        return self.notes[note]["center"]

    def set_bass_outline_color(self, color):
        self.itemconfigure(self.bass["id"], outline=color)

    def set_bass_position_and_radius(self, note, radius):
        self.bass["note"] = note
        self.bass["radius"] = radius
        center = self.get_note_position(note)
        x0, x1 = center["x"] - radius, center["x"] + radius
        y0, y1 = center["y"] - radius, center["y"] + radius
        self.coords(self.bass["id"], x0, y0, x1, y1)

    def set_bass_width(self, width):
        self.itemconfigure(self.bass["id"], width=width)

    def set_note_color(self, note, color):
        self.itemconfigure(self.notes[note]["id"], fill=color, outline=color)

    def set_note_outline_color(self, note, color):
        self.itemconfigure(self.notes[note]["id"], outline=color)

    def set_note_hollow(self, note):
        self.itemconfigure(self.notes[note]["id"], fill="")

    def set_note_radius(self, note, radius):
        self.notes[note]["radius"] = radius
        center = self.get_note_position(note)
        x = center["x"]
        y = center["y"]
        self.coords(
            self.notes[note]["id"], x - radius, y - radius, x + radius, y + radius
        )

    def set_note_not_in_scale(self, note):
        self.set_note_hollow(note)
        self.set_note_outline_color(note, "")

    def set_note_in_scale(self, note, is_root):
        color = COLORS["chordDim"]
        if is_root:
            color = COLORS["rootDim"]
        self.set_note_radius(note, self.small_note_radius)
        self.set_note_hollow(note)
        self.set_note_outline_color(note, color)

    def set_note_shadow(self, note, is_root=False):
        color = COLORS["chord"]
        if is_root:
            color = COLORS["root"]
        self.set_note_radius(note, self.large_note_radius)
        self.set_note_hollow(note)
        self.set_note_outline_color(note, color)

    def set_note_played(self, note, is_root=False):
        color = COLORS["chord"]
        if is_root:
            color = COLORS["root"]
        self.set_note_radius(note, self.large_note_radius)
        self.set_note_color(note, color)

    def convert_note(self, note):
        return ((note % 12) + (12 - self.key)) % 12

    def set_key(self, key):
        self.key = key
        self.itemconfigure(self.key_text, text=self.note_names[self.key])

    def set_scale(self, scale):
        self.scale_notes = scale
        for note in range(12):
            if note in self.scale_notes:
                is_root = note == self.root
                self.set_note_in_scale(note, is_root)
            else:
                self.set_note_not_in_scale(note)

    def set_chord(self, chord_types, root_type):
        self.root = self.convert_note(root_type)
        self.set_scale(self.scale_notes)
        self.chord = [self.convert_note(i) for i in chord_types]
        # self.chord_name.set(chord_types, root_type)

    def set_chord_shadow(self):
        for note in self.chord:
            is_root = note == self.root
            self.set_note_shadow(note, is_root)

    def play_chord(self):
        for note in self.chord:
            is_root = note == self.root
            self.set_note_played(note, is_root)

    def set_bass_shadow(self, note):
        note = self.convert_note(note)
        color = COLORS["chord"]
        if note == self.root:
            color = COLORS["root"]
        self.set_bass_position_and_radius(note, self.bass_note_shadow_radius)
        self.set_bass_width(self.bass_outline_shadow_width)
        self.set_bass_outline_color(color)

    def play_bass(self, note):
        note = self.convert_note(note)
        color = COLORS["chord"]
        if note == self.root:
            color = COLORS["root"]
        self.set_bass_position_and_radius(note, self.bass_note_played_radius)
        self.set_bass_width(self.bass_outline_played_width)
        self.set_bass_outline_color(color)

    # make this set_modulation - can work for forward and backwards + left to right mods!
    def set_modulation(self, new_scale, side):
        print("new Scale: ")
        print(new_scale)
        self.modulation_state = {
            "side": side,
            "oldScale": self.scale_notes,
            "newScale": new_scale,
            "status": "startAnimation",
            "startTime": time.time(),
        }
        self.set_scale(new_scale)
