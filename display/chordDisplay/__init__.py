import tkinter as tk
import math
from constants import *
import time
import math
from ..displayConstants import COLORS, FONTS

class ChordDisplay(tk.Canvas):
  height = 350
  width = 300
  radius = 120

  smallNoteRadius = 16
  largeNoteRadius = 18
  outlineWidth = 4

  bassRadius = 120
  bassNoteShadowRadius = 21
  bassNotePlayedRadius = 23
  bassDash = ()
  bassOutlineShadowWidth = 6
  bassOutlinePlayedWidth = 10

  modAnimationLength = 0.5

  keyTextOffset = -60
  keyTextFontSize = 30

  noteNames = ["C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B"]

  def __init__(self, master=None):
    super().__init__(master, width=self.width, height=self.height, highlightthickness=0, relief="flat", bg="#000000")
    self.scale = [0, 2, 4, 5, 7, 9, 11]
    self.modulationState = {
      "oldScale": [0, 2, 4, 5, 7, 9, 11],
      "newScale": None,
      "status": "none",
      "startTime": 0
    }
    self.animationInProgress = False
    self.master = master
    self.key = 0
    self.root = 0
    self.bassNote = 0
    self.notes = self.createNotes()
    self.keyText = self.createKeyText()
    self.bass = self.createBassNote()
    #self.bassPlayed = self.createBassPlayedNote()
    self.pack(side="right", pady=(30, 0), padx=(0,80))

  def createKeyText(self):
    x = self.width / 2
    y = self.notes[0]["center"]["y"] + self.keyTextOffset
    return self.create_text(x, y, fill=COLORS["chord"], text=self.noteNames[self.key], font=FONTS["big"])

  def createBassNote(self):
    center = self.notes[0]["center"]
    x0, x1 = center["x"] - self.bassNoteShadowRadius, center["x"] + self.bassNoteShadowRadius
    y0, y1 = center["y"] - self.bassNoteShadowRadius, center["y"] + self.bassNoteShadowRadius
    bassNote = self.create_oval(x0, y0, x1, y1, 
      fill='', 
      outline=COLORS["root"], 
      dash=self.bassDash, 
      width=self.bassOutlineShadowWidth
    )
    return bassNote

  def createNotes(self):
    notes = []
    centerX = self.width / 2
    centerY = self.height - centerX
    for i in range(0, 12):
      color = ''
      if self.scale.count(i) != 0:
        color = COLORS["chordDim"]
      theta = ((i*-2*math.pi) / 12) + (0.5*math.pi)
      x = centerX + (self.radius*math.cos(theta))
      y = centerY - (self.radius*math.sin(theta))
      x0, x1 = x - self.smallNoteRadius, x + self.smallNoteRadius
      y0, y1 = y - self.smallNoteRadius, y + self.smallNoteRadius

      note = {
        "id": self.create_oval(
          x0, y0, x1, y1, 
          width=self.outlineWidth,
          fill='',
          outline = color
        ),
        "center": { "x": x, "y": y },
        "radius": self.smallNoteRadius
      }
      notes.append(note)
    return notes

  def setNotePosition(self, note, x, y):
    r = self.notes[note]["radius"]
    x0, x1 = x - r, x + r
    y0, y1 = y - r, y + r
    self.coords(self.notes[note]["id"],x0, y0, x1, y1)

  def runAnimationStep(self):
    if self.modulationState["status"] == "startAnimation":
      t = time.time() - self.modulationState["startTime"]
      for note in self.modulationState["scale"]:
        center = self.getNotePosition(self, note)
        self.setNotePosition(note, center["x"], center["y"])
      if t > self.modAnimationLength:
        self.modulationState["status"] = "active"

  def distance(self, x0, y0, x1, y1):
    return math.sqrt(((x1 - x0)**2) + ((y0 - y1)**2))

  def calculateAnimatedNoteDistance(self, D, t):
    if D == 0: return 0
    T = self.modAnimationLength
    if t <= T / 2:
      return ((2 * D) / (T ** 2)) * (t ** 2)
    elif t <= T:
      return (((-2 * D) / (T ** 2)) * (t ** 2)) + ((4 * D * t) / T)
    else:
      return D

  def getNotePosition(self, note):
    if self.modulationState["status"] == "none":
      return self.notes[note]["center"]
    elif self.modulationState["status"] == "startAnimation":
      newScale = self.modulationState["newScale"]
      oldScale = self.modulationState["oldScale"]
      if note in newScale:
        t = time.time() - self.modulationState["startTime"]
        index = newScale.index(note)
        oldNote = oldScale[index]
        center0 = self.notes[oldNote]["center"]
        center1 = self.notes[note]["center"]
        x0, y0 = center0["x"], center0["y"]
        x1, y1 = center1["x"], center1["y"]
        D = self.distance(x0, y0, x1, y1)
        d = self.calculateAnimatedNoteDistance(D, t)
        x = ((x1 - x0) * d) / D
        y = ((y1 - y0) * d) / D
        return {"x": x, "y": y}
      else:
        return self.notes[note]["center"]

  def setBassOutlineColor(self, color):
    self.itemconfigure(self.bass, outline=color)

  def setBassPositionAndRadius(self, note, radius):
    center = self.notes[note]["center"]
    x0, x1 = center["x"] - radius, center["x"] + radius
    y0, y1 = center["y"] - radius, center["y"] + radius
    self.coords(self.bass, x0, y0, x1, y1)

  def setBassWidth(self, width):
    self.itemconfigure(self.bass, width=width)

  def setNoteColor(self, note, color):
    self.itemconfigure(self.notes[note]["id"], fill=color, outline=color)

  def setNoteOutlineColor(self, note, color):
    self.itemconfigure(self.notes[note]["id"], outline=color)

  def setNoteHollow(self, note):
    self.itemconfigure(self.notes[note]["id"], fill='')
  
  def setNoteRadius(self, note, radius):
    self.notes[note]["radius"] = radius
    center = self.getNotePosition(note)
    x = center["x"]
    y = center["y"]
    self.coords(self.notes[note]["id"], x - radius, y - radius, x + radius, y + radius)

  def setNoteNotInScale(self, note):
    self.setNoteHollow(note)
    self.setNoteOutlineColor(note, '')

  def setNoteInScale(self, note, isRoot):
    color = COLORS["chordDim"]
    if isRoot: color = COLORS["rootDim"]
    self.setNoteRadius(note, self.smallNoteRadius)
    self.setNoteHollow(note)
    self.setNoteOutlineColor(note, color)

  def setNoteShadow(self, note, isRoot=False):
    color = COLORS["chord"]
    if isRoot: color = COLORS["root"]
    self.setNoteRadius(note, self.largeNoteRadius)
    self.setNoteHollow(note)
    self.setNoteOutlineColor(note, color)

  def setNotePlayed(self, note, isRoot=False):
    color = COLORS["chord"]
    if isRoot: color = COLORS["root"]
    self.setNoteRadius(note, self.largeNoteRadius)
    self.setNoteColor(note, color)

  def convertNote(self, note):
    return ((note % 12) + (12-self.key)) % 12

  def setKey(self, key):
    self.key = key
    self.itemconfigure(self.keyText, text=self.noteNames[self.key])

  def setScale(self, scale):
    self.scale = scale
    for note in range(0, 12):
      if note in self.scale:
        isRoot = note == self.root
        self.setNoteInScale(note, isRoot)
      else:
        self.setNoteNotInScale(note)

  def setChord(self, chordTypes, rootType):
    self.root = self.convertNote(rootType)
    self.setScale(self.scale)
    chord = []
    for i in chordTypes:
      chord.append(self.convertNote(i))
    self.chord = chord

  def setChordShadow(self):
    for note in self.chord:
      isRoot = note == self.root
      self.setNoteShadow(note, isRoot)

  def playChord(self):
    for note in self.chord:
      isRoot = note == self.root
      self.setNotePlayed(note, isRoot)

  def setBassShadow(self, note):
    note = self.convertNote(note)
    color = COLORS["chord"]
    if note == self.root: color = COLORS["root"]
    self.setBassPositionAndRadius(note, self.bassNoteShadowRadius)
    self.setBassWidth(self.bassOutlineShadowWidth)
    self.setBassOutlineColor(color)

  def playBass(self, note):
    note = self.convertNote(note)
    color = COLORS["chord"]
    if note == self.root: color = COLORS["root"]
    self.setBassPositionAndRadius(note, self.bassNotePlayedRadius)
    self.setBassWidth(self.bassOutlinePlayedWidth)
    self.setBassOutlineColor(color)

  def startModulation(self, map):
    clamped = []
    for degree in map:
      clamped.append(degree % 12)
    self.modulationState = {
      "oldScale": self.scale,
      "newScale": clamped,
      "status": "startAnimation",
      "startTime": time.time()
    }
    self.setScale(clamped)

