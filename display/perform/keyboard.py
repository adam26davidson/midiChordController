import tkinter as tk

from ..displayConstants import COLORS


class Keyboard(tk.Canvas):

  arrow_x_padding = 1
  small_arrow_width = 10
  small_arrow_height = 8
  large_arrow_width = 15
  large_arrow_height = 12

  key_x_offset = 25
  white_key_y_offset = 17
  key_diameter = 20
  small_radius = 2
  medium_radius = 5
  large_radius = 7
  key_outline_width = 2

  width = 770
  height = 37

  black_note_types = [1, 3, 6, 8, 10]
  key_range = range(36, 97)
  min_key = 36
  max_key = 96

  chord_color_dim = COLORS["chordDim"]
  root_color_dim = COLORS["rootDim"]
  chord_color = COLORS["chord"]
  root_color = COLORS["root"]

  def __init__(self, master=None):
    super().__init__(master, width=self.width, height=self.height, highlightthickness=0, relief="flat", bg="#000000")
    self.master = master
    self.keys = self.create_keys()
    self.arrows = self.create_arrows()
    self.keys_out_of_range = {
      "above": {"played": [], "shadow": []},
      "below": {"played": [], "shadow": []}
    }
    self.pack(side="bottom", pady=(0,20), padx=(15, 15))

    self.root = 0
    self.chord = None

  def create_arrows(self):
    xl0 = self.arrow_x_padding + ((self.large_arrow_width - self.small_arrow_width)/ 2)
    y0 = self.height / 2
    xl1 = xl0 + self.small_arrow_width
    y1 = y0 - (self.small_arrow_height / 2)
    xl2 = xl1
    y2 = y0 + (self.small_arrow_height / 2)

    left_arrow = {
      "id": self.create_polygon(
        xl0, y0, xl1, y1, xl2, y2,
        joinstyle="round",
        smooth=0,
        width=self.key_outline_width,
        fill='',
        outline=self.chord_color_dim
      ),
      "center": {
        "x": xl0 + (self.small_arrow_width / 2),
        "y": y0
      }
    }

    xr0 = self.width - xl0
    xr1 = self.width - xl1
    xr2 = xr1

    right_arrow = {
      "id": self.create_polygon(
        xr0, y0, xr1, y1, xr2, y2,
        joinstyle="round",
        smooth=0,
        width=self.key_outline_width,
        fill='',
        outline=self.chord_color_dim
      ),
      "center": {
        "x": xr0 - (self.small_arrow_width / 2),
        "y": y0
      }
    }

    return {"left": left_arrow, "right": right_arrow}

  def create_keys(self):
    keys = {}
    white_key_index = 0
    for i in self.key_range:
      if self.black_note_types.count(i % 12) == 1:
        x_l = self.key_x_offset + self.key_diameter*white_key_index - self.small_radius
        y_t = (self.key_diameter / 2)  - self.small_radius
      else:
        x_l = self.key_x_offset + self.key_diameter*(white_key_index + 0.5) - self.small_radius
        y_t = ((self.key_diameter / 2) - self.small_radius) + self.white_key_y_offset
        white_key_index += 1
      x_r = x_l + (2 * self.small_radius)
      y_b = y_t + (2 * self.small_radius)

      key = {
          "id": self.create_oval(
            x_l, y_t, x_r, y_b,
            fill=self.chord_color,
            outline=self.chord_color,
            width=self.key_outline_width),
          "center": {
            "x": x_l + self.small_radius / 2,
            "y": y_t + self.small_radius / 2
          }
        }
      keys[i] = key

    return keys

  def set_arrow_color(self, side, color):
    self.itemconfigure(
      self.arrows[side]["id"],
      fill=color,
      outline=color
    )

  def set_arrow_hollow(self, side):
    self.itemconfigure(self.arrows[side]["id"], fill='')

  def set_arrow_outline_color(self, side, color):
    self.itemconfigure(self.arrows[side]["id"], outline=color)

  def set_arrow_size(self, side, size):

    height = self.large_arrow_height
    width = self.large_arrow_width
    if size == "small":
      height = self.small_arrow_height
      width = self.small_arrow_width

    center = self.arrows[side]["center"]
    y0 = center["y"]
    y1 = y0 - (height / 2)
    y2 = y0 + (height / 2)

    sign = 1
    if side == "right":
      sign = -1

    x0 = center["x"] - sign * (width / 2)
    x1 = x0 + sign * width
    self.coords(self.arrows[side]["id"], x0, y0, x1, y1, x1, y2)

  def contains_root(self, notes):
    contained = False
    for note in notes:
      if note % 12 == self.root:
        contained = True
        break
    return contained

  def reset_key_out_of_range(self, note):
    side = "below"
    if note < self.min_key:
      side = "above"
    for type in "shadow", "played":
      if self.keys_out_of_range[side][type].count(note) > 0:
        self.keys_out_of_range[side][type].remove(note)
    no_keys_played = self.keys_out_of_range[side]["played"].count(note) == 0
    no_keys_shadow = self.keys_out_of_range[side]["shadow"].count(note) == 0
    return no_keys_played and no_keys_shadow

  def set_key_out_of_range_shadow(self, note):
    side = "below"
    if note < self.min_key:
      side = "above"
    if self.keys_out_of_range[side]["played"].count(note) > 0:
      self.keys_out_of_range[side]["played"].remove(note)
    if self.keys_out_of_range[side]["shadow"].count(note) == 0:
      self.keys_out_of_range[side]["shadow"].append(note)
    no_keys_played = self.keys_out_of_range[side]["played"].count(note) == 0
    root_is_shadow = self.contains_root(self.keys_out_of_range[side]["shadow"])
    return no_keys_played, root_is_shadow

  def set_key_out_of_range_played(self, note):
    side = "below"
    if note < self.min_key:
      side = "above"
    if self.keys_out_of_range[side]["shadow"].count(note) > 0:
      self.keys_out_of_range[side]["shadow"].remove(note)
    if self.keys_out_of_range[side]["played"].count(note) == 0:
      self.keys_out_of_range[side]["played"].append(note)
    root_is_played = self.contains_root(self.keys_out_of_range[side]["played"])
    return root_is_played

  def set_arrow_clear(self, side):
    self.set_arrow_size(side, "small")
    self.set_arrow_hollow(side)
    self.set_arrow_outline_color(side, self.chord_color_dim)

  def set_arrow_shadow(self, side, is_root=False):
    color = self.chord_color
    if is_root:
      color = self.root_color
    self.set_arrow_size(side, "large")
    self.set_arrow_hollow(side)
    self.set_arrow_outline_color(side, color)

  def set_arrow_played(self, side, is_root=False):
    color = self.chord_color
    if is_root:
      color = self.root_color
    self.set_arrow_size(side, "large")
    self.set_arrow_color(side, color)

  def set_key_color(self, note, color):
    self.itemconfigure(self.keys[note]["id"], fill=color)
    self.itemconfigure(self.keys[note]["id"], outline=color)

  def set_key_hollow(self, note):
    self.itemconfigure(self.keys[note]["id"], fill='')

  def set_key_outline_color(self, note, color):
    self.itemconfigure(self.keys[note]["id"], outline=color)

  def set_key_radius(self, note, radius):
    x = self.keys[note]["center"]["x"]
    y = self.keys[note]["center"]["y"]
    self.coords(self.keys[note]["id"], x - radius, y - radius, x + radius, y + radius)

  def set_key_clear(self, note):
    self.set_key_radius(note, self.small_radius)
    self.set_key_color(note, self.chord_color_dim)

  def set_key_chord(self, note, is_root=False):
    color = self.chord_color_dim
    if is_root:
      color = self.root_color_dim
    self.set_key_radius(note, self.medium_radius)
    self.set_key_hollow(note)
    self.set_key_outline_color(note, color)

  def set_key_shadow(self, note, is_root=False):
    color = self.chord_color
    if is_root:
      color = self.root_color
    self.set_key_radius(note, self.large_radius)
    self.set_key_hollow(note)
    self.set_key_outline_color(note, color)

  def set_key_played(self, note, is_root=False):
    color = self.chord_color
    if is_root:
      color = self.root_color
    self.set_key_radius(note, self.large_radius)
    self.set_key_color(note, color)

  def reset_all(self):
    self.clear_all()
    if self.chord:
      self.set_chord(self.chord, self.root)

  def set_chord(self, note_types, root_type):
    self.clear_all()
    self.chord = note_types
    self.root = root_type
    for note in self.key_range:
      if note % 12 == root_type:
        self.set_key_chord(note, is_root=True)
      elif note_types.count(note % 12) > 0:
        self.set_key_chord(note)

  def clear_all(self):
    for note in self.key_range:
      self.set_key_clear(note)

  def reset(self, notes):
    for note in notes:
      if note in self.key_range:
        if note % 12 == self.root:
          self.set_key_chord(note, is_root=True)
        elif self.chord.count(note % 12) > 0:
          self.set_key_chord(note)
        else:
          self.set_key_clear(note)
      else:
        side = "left"
        if note > self.max_key:
          side = "right"
        all_keys_off = self.reset_key_out_of_range(note)
        if all_keys_off:
          self.set_arrow_clear(side)

  def set_shadow(self, notes):
    for note in notes:
      is_root = note % 12 == self.root
      if note in self.key_range:
          self.set_key_shadow(note, is_root=is_root)
      else:
        side = "left"
        if note > self.max_key:
          side = "right"
        no_keys_played, root_is_shadow = self.set_key_out_of_range_shadow(note)
        if no_keys_played:
          self.set_arrow_shadow(side, is_root=root_is_shadow)

  def play(self, notes):
    for note in notes:
      is_root = note % 12 == self.root
      if note in self.key_range:
          self.set_key_played(note, is_root=is_root)
      else :
        side = "left"
        if note > self.max_key:
          side = "right"
        root_is_played = self.set_key_out_of_range_played(note)
        self.set_arrow_played(side, is_root=root_is_played)



