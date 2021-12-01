import tkinter as tk

class Keyboard(tk.Canvas):

  smallRadius = 2
  mediumRadius = 4
  largeRadius = 7

  arrowXPadding = 2
  smallArrowWidth = 15
  smallArrowHeight = 12
  largeArrowWidth = 20
  largeArrowHeight = 16

  keyXOffset = 30
  whiteKeyYOffset = 17
  keyDiameter = 20
  keyOutlineWidth = 2

  width = 780
  height = 37
  blackNoteTypes = [1, 3, 6, 8, 10]
  keyRange = range(36, 97)
  minKey = 36
  maxKey = 97

  chordColorDim = "#828282"
  rootColorDim = "#ab9346"
  chordColor = "#ffffff"
  rootColor = "#ffc400"

  def __init__(self, master=None):
    super().__init__(master, width=self.width, height=self.height, highlightthickness=0, relief="flat", bg="#000000")
    self.master = master
    self.keys = self.createKeys()
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

    self.rightArrow = {
      "id": self.create_polygon(
        xl0, y0, xl1, y1, xl2, y2,
        joinstyle="round",
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

    self.rightArrow = {
      "id": self.create_polygon(
        xr0, y0, xr1, y1, xr2, y2,
        joinstyle="round",
        width=self.keyOutlineWidth,
        fill='',
        outline=self.chordColorDim
      ),
      "center": {
        "x": xr0 - (self.smallArrowWidth / 2),
        "y": y0
      }
    }

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
  
  def setShadow(self, notes):
    for note in notes:
      if note in self.keyRange:
        if note % 12 == self.root:
          self.setKeyShadow(note, isRoot=True)
        else:
          self.setKeyShadow(note)

  def play(self, notes):
    for note in notes:
      if note in self.keyRange:
        if note % 12 == self.root:
          self.setKeyPlayed(note, isRoot=True)
        else:
          self.setKeyPlayed(note)
      else:
        # TODO add indication that notes are played outside keyboard range
        pass

  