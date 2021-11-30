import tkinter as tk

class Keyboard(tk.Canvas):

  smallRadius = 2
  mediumRadius = 4
  largeRadius = 7
  bassRadius = 9
  whiteKeyYOffset = 20
  keyDiameter = 20
  keyOutlineWidth = 2
  width = 720
  height = 40
  blackHeight = 27
  blackNoteTypes = [1, 3, 6, 8, 10]
  keyRange = range(36, 97)
  minKey = 21
  maxKey = 108

  blackColor = "#262626"
  whiteColor = "#262626"

  shadowColor = "#858585"
  rootShadowColor = "#567e85"

  playedColor = "#ffffff"
  rootPlayedColor = "#00d9ff"

  chordColor = "#ffffff"
  rootColor = "#ffc400"

  def __init__(self, master=None):
    super().__init__(master, width=self.width, height=self.height, highlightthickness=0, relief="flat", bg="#000000")
    self.master = master
    self.keys = self.createKeys()
    self.pack(side="bottom", pady=(0,20))

    self.root = 0
    self.chord = None

  def createKeys(self):
    keys = {}
    whiteKeyIndex = 0
    for i in self.keyRange:
      if self.blackNoteTypes.count(i % 12) == 1:
        xL = self.keyDiameter*whiteKeyIndex - self.smallRadius
        yT = 0
      else:
        xL = self.keyDiameter*(whiteKeyIndex + 0.5) - self.smallRadius
        yT = self.whiteKeyYOffset
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
            "x": xL + self.keyDiameter / 2, 
            "y": yT + self.keyDiameter / 2
          }
        }
      keys[i] = key

    #Creates count octaves of a specified black key note
    # def createBlackKeys(xOffset, midiOffset, count, noteName):
    #   for i in range(count):
    #     xL = xOffset + ( i * 14 * 7)
    #     xR = xL + 8
    #     yT = 2
    #     yB = self.blackHeight + 2
    #     key = {
    #       "id": self.create_polygon(xL, yT, xL, yB, xR, yB, xR, yT, fill=self.blackColor),
    #       "color": "black",
    #       "note": noteName 
    #     }
    #     keys[midiOffset + (12 * i)] = key

    #Creates count octaves of a specified white key note
    # def createWhiteKeys(xOffset, midiOffset, rNotch, lNotch, count, noteName):
    #   for i in range(count):
    #     xL = xOffset + ( i * 14 * 7)
    #     xR = xL + 12
    #     xLN = xL + lNotch
    #     xRN = xR - rNotch
    #     yN = self.blackHeight + 4
    #     yT = 2
    #     yB = self.height - 2
    #     key = {
    #       "id": self.create_polygon(xLN, yT, xLN, yN, xL, yN, xL, yB, xR, yB, xR, yN, xRN, yN, xRN, yT, fill=self.whiteColor),
    #       "color": "white",
    #       "note": noteName 
    #     }
    #     keys[midiOffset + (12 * i)] = key

    # createBlackKeys(13, 22, 8, "Bb") #Bb0-Bb7
    # createBlackKeys(38, 25, 7, "Db") #Db1-Db7
    # createBlackKeys(54, 27, 7, "Eb") #Eb1-Eb7
    # createBlackKeys(79, 30, 7, "Gb") #Gb1-Gb7
    # createBlackKeys(95, 32, 7, "Ab") #Ab1-Ab7

    # createWhiteKeys(2, 21, 3, 0, 1, "A") #A0
    # createWhiteKeys(16, 23, 0, 7, 8, "B") #B0-B7
    # createWhiteKeys(30, 24, 6, 0, 7, "C") #C1-C7
    # createWhiteKeys(44, 26, 4, 4, 7, "D") #D1-D7
    # createWhiteKeys(58, 28, 0, 6, 7, "E") #E1-E7
    # createWhiteKeys(72, 29, 7, 0, 7, "F") #F1-F7
    # createWhiteKeys(86, 31, 5, 3, 7, "G") #G1-G7
    # createWhiteKeys(100, 33, 3, 5, 7, "A") #A1-A7
    # createWhiteKeys(2+(14*51), 108, 0, 0, 1, "C") #C8

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
    self.setKeyColor(note, self.chordColor)

  def setKeyChord(self, note, isRoot=False):
    color = self.chordColor
    if isRoot: color = self.rootColor
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

  