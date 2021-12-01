import tkinter as tk
from .displayConstants import COLORS

class Keyboard(tk.Canvas):

  arrowXPadding = 1
  smallArrowWidth = 10
  smallArrowHeight = 8
  largeArrowWidth = 15
  largeArrowHeight = 12

  keyXOffset = 25
  whiteKeyYOffset = 17
  keyDiameter = 20
  smallRadius = 2
  mediumRadius = 5
  largeRadius = 7
  keyOutlineWidth = 2

  width = 770
  height = 37

  blackNoteTypes = [1, 3, 6, 8, 10]
  keyRange = range(36, 97)
  minKey = 36
  maxKey = 96

  chordColorDim = COLORS["chordDim"]
  rootColorDim = COLORS["rootDim"]
  chordColor = COLORS["chord"]
  rootColor = COLORS["root"]

  def __init__(self, master=None):
    super().__init__(master, width=self.width, height=self.height, highlightthickness=0, relief="flat", bg="#000000")
    self.master = master
    self.keys = self.createKeys()
    self.arrows = self.createArrows()
    self.keysOutOfRange = {
      "above": {"played": [], "shadow": []},
      "below": {"played": [], "shadow": []}
    }
    self.pack(side="bottom", pady=(0,20))

    self.root = 0
    self.chord = None

  def createArrows(self):
    xl0 = self.arrowXPadding + ((self.largeArrowWidth - self.smallArrowWidth)/ 2)
    y0 = self.height / 2
    xl1 = xl0 + self.smallArrowWidth
    y1 = y0 - (self.smallArrowHeight / 2)
    xl2 = xl1
    y2 = y0 + (self.smallArrowHeight / 2)

    leftArrow = {
      "id": self.create_polygon(
        xl0, y0, xl1, y1, xl2, y2,
        joinstyle="round",
        smooth=0,
        width=self.keyOutlineWidth,
        fill='',
        outline=self.chordColorDim
      ),
      "center": {
        "x": xl0 + (self.smallArrowWidth / 2),
        "y": y0
      }
    }

    xr0 = self.width - xl0
    xr1 = self.width - xl1
    xr2 = xr1

    rightArrow = {
      "id": self.create_polygon(
        xr0, y0, xr1, y1, xr2, y2,
        joinstyle="round",
        smooth=0,
        width=self.keyOutlineWidth,
        fill='',
        outline=self.chordColorDim
      ),
      "center": {
        "x": xr0 - (self.smallArrowWidth / 2),
        "y": y0
      }
    }

    return {"left": leftArrow, "right": rightArrow}

  def createKeys(self):
    keys = {}
    whiteKeyIndex = 0
    for i in self.keyRange:
      if self.blackNoteTypes.count(i % 12) == 1:
        xL = self.keyXOffset + self.keyDiameter*whiteKeyIndex - self.smallRadius
        yT = (self.keyDiameter / 2)  - self.smallRadius
      else:
        xL = self.keyXOffset + self.keyDiameter*(whiteKeyIndex + 0.5) - self.smallRadius
        yT = ((self.keyDiameter / 2) - self.smallRadius) + self.whiteKeyYOffset
        whiteKeyIndex += 1
      xR = xL + (2 * self.smallRadius)
      yB = yT + (2 * self.smallRadius)

      key = {
          "id": self.create_oval(
            xL, yT, xR, yB, 
            fill=self.chordColor, 
            outline=self.chordColor, 
            width=self.keyOutlineWidth),
          "center": {
            "x": xL + self.smallRadius / 2, 
            "y": yT + self.smallRadius / 2
          }
        }
      keys[i] = key

    return keys 

  def setArrowColor(self, side, color):
    self.itemconfigure(
      self.arrows[side]["id"], 
      fill=color,
      outline=color
    )

  def setArrowHollow(self, side):
    self.itemconfigure(self.arrows[side]["id"], fill='')

  def setArrowOutlineColor(self, side, color):
    self.itemconfigure(self.arrows[side]["id"], outline=color)

  def setArrowSize(self, side, size):

    height = self.largeArrowHeight
    width = self.largeArrowWidth
    if size == "small":
      height = self.smallArrowHeight
      width = self.smallArrowWidth

    center = self.arrows[side]["center"]
    y0 = center["y"]
    y1 = y0 - (height / 2)
    y2 = y0 + (height / 2)

    sign = 1
    if side == "right": sign = -1

    x0 = center["x"] - sign * (width / 2)
    x1 = x0 + sign * width
    self.coords(self.arrows[side]["id"], x0, y0, x1, y1, x1, y2)

  def resetKeyOutOfRange(self, note):
    side = "below"
    if note < self.minKey: side = "above"
    for type in "shadow", "played":
      if self.keysOutOfRange[side][type].count(note) > 0:
        self.keysOutOfRange[side][type].remove(note)
    noKeysPlayed = self.keysOutOfRange[side]["played"].count(note) == 0
    noKeysShadow = self.keysOutOfRange[side]["shadow"].count(note) == 0
    return noKeysPlayed and noKeysShadow

  def setKeyOutOfRangeShadow(self, note):
    side = "below"
    if note < self.minKey: side = "above"
    if self.keysOutOfRange[side]["played"].count(note) > 0:
      self.keysOutOfRange[side]["played"].remove(note)
    if self.keysOutOfRange[side]["shadow"].count(note) == 0:
      self.keysOutOfRange[side]["shadow"].append(note)
    noKeysPlayed = self.keysOutOfRange[side]["played"].count(note) == 0
    rootIsShadow = self.keysOutOfRange[side]["shadow"].count(self.root) == 1
    return noKeysPlayed, rootIsShadow

  def setKeyOutOfRangePlayed(self, note):
    side = "below"
    if note < self.minKey: side = "above"
    if self.keysOutOfRange[side]["shadow"].count(note) > 0:
      self.keysOutOfRange[side]["shadow"].remove(note)
    if self.keysOutOfRange[side]["played"].count(note) == 0:
      self.keysOutOfRange[side]["played"].append(note)
    rootIsPlayed = self.keysOutOfRange[side]["played"].count(self.root) == 1
    return rootIsPlayed

  def setArrowClear(self, side):
    self.setArrowSize(side, "small")
    self.setArrowHollow(side)
    self.setArrowOutlineColor(side, self.chordColorDim)

  def setArrowShadow(self, side, isRoot=False):
    color = self.chordColor
    if isRoot: color = self.rootColor
    self.setArrowSize(side, "large")
    self.setArrowHollow(side)
    self.setArrowOutlineColor(side, color)

  def setArrowPlayed(self, side, isRoot=False):
    color = self.chordColor
    if isRoot: color = self.rootColor
    self.setArrowSize(side, "large")
    self.setArrowColor(side, color)

  def setKeyColor(self, note, color):
    self.itemconfigure(self.keys[note]["id"], fill=color)
    self.itemconfigure(self.keys[note]["id"], outline=color)
  
  def setKeyHollow(self, note):
    self.itemconfigure(self.keys[note]["id"], fill='')

  def setKeyOutlineColor(self, note, color):
    self.itemconfigure(self.keys[note]["id"], outline=color)

  def setKeyRadius(self, note, radius):
    x = self.keys[note]["center"]["x"]
    y = self.keys[note]["center"]["y"]
    self.coords(self.keys[note]["id"], x - radius, y - radius, x + radius, y + radius)

  def setKeyClear(self, note):
    self.setKeyRadius(note, self.smallRadius)
    self.setKeyColor(note, self.chordColorDim)

  def setKeyChord(self, note, isRoot=False):
    color = self.chordColorDim
    if isRoot: color = self.rootColorDim
    self.setKeyRadius(note, self.mediumRadius)
    self.setKeyHollow(note)
    self.setKeyOutlineColor(note, color)
  
  def setKeyShadow(self, note, isRoot=False):
    color = self.chordColor
    if isRoot: color = self.rootColor
    self.setKeyRadius(note, self.largeRadius)
    self.setKeyHollow(note)
    self.setKeyOutlineColor(note, color)
  
  def setKeyPlayed(self, note, isRoot=False):
    color = self.chordColor
    if isRoot: color = self.rootColor
    self.setKeyRadius(note, self.largeRadius)
    self.setKeyColor(note, color)

  def resetAll(self):
    self.clearAll()
    if self.chord:
      self.setChord(self.chord, self.root)

  def setChord(self, noteTypes, rootType):
    self.clearAll()
    self.chord = noteTypes
    self.root = rootType
    for note in self.keyRange:
      if note % 12 == rootType:
        self.setKeyChord(note, isRoot=True)
      elif noteTypes.count(note % 12) > 0:
        self.setKeyChord(note)

  def clearAll(self):
    for note in self.keyRange:
      self.setKeyClear(note)

  def reset(self, notes):
    for note in notes:
      if note in self.keyRange:
        if note % 12 == self.root:
          self.setKeyChord(note, isRoot=True)
        elif self.chord.count(note % 12) > 0:
          self.setKeyChord(note)
        else:
          self.setKeyClear(note)
      else:
        side = "left"
        if note > self.maxKey: side = "right"
        allKeysOff = self.resetKeyOutOfRange(note)
        if allKeysOff:
          self.setArrowClear(side)
  
  def setShadow(self, notes):
    for note in notes:
      isRoot = note % 12 == self.root
      if note in self.keyRange:
          self.setKeyShadow(note, isRoot=isRoot)
      else:
        side = "left"
        if note > self.maxKey: side = "right"
        noKeysPlayed, rootIsShadow = self.setKeyOutOfRangeShadow(note)
        if noKeysPlayed:
          self.setArrowShadow(side, isRoot=rootIsShadow)

  def play(self, notes):
    for note in notes:
      isRoot = note % 12 == self.root
      if note in self.keyRange:
          self.setKeyPlayed(note, isRoot=isRoot)
      else :
        side = "left"
        if note > self.maxKey: side = "right"
        rootIsPlayed = self.setKeyOutOfRangePlayed(note)
        self.setArrowPlayed(side, isRoot=rootIsPlayed)

        

  