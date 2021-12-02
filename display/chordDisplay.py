import tkinter as tk
import math
from constants import *
from .displayConstants import COLORS, FONTS

class ChordDisplay(tk.Canvas):
  height = 350
  width = 350
  radius = 120

  smallNoteRadius = 13
  largeNoteRadius = 18
  outlineWidth = 3

  bassRadius = 120
  bassNoteShadowRadius = 21
  bassNotePlayedRadius = 24
  bassDash = ()
  bassOutlineShadowWidth = 6
  bassOutlinePlayedWidth = 12

  keyTextOffset = -60
  keyTextFontSize = 30

  noteNames = ["C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B"]

  def __init__(self, master=None):
    super().__init__(master, width=self.width, height=self.height, highlightthickness=0, relief="flat", bg="#000000")
    self.master = master
    self.key = 0
    self.root = 0
    self.bassNote = 0
    self.scale = [0, 2, 4, 5, 7, 9, 11]
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
    centerX = self.width / 2
    centerY = self.height - centerX
    theta = ((0*-2*math.pi) / 12) + (0.5*math.pi)
    x = centerX + (self.bassRadius*math.cos(theta))
    y = centerY - (self.bassRadius*math.sin(theta))
    x0, x1 = x - self.bassNoteShadowRadius, x + self.bassNoteShadowRadius
    y0, y1 = y - self.bassNoteShadowRadius, y + self.bassNoteShadowRadius
    bassNote = self.create_oval(x0, y0, x1, y1, 
      fill='', 
      outline=COLORS["root"], 
      dash=self.bassDash, 
      width=self.bassOutlineShadowWidth
    )
    return bassNote

  # def createBassPlayedNote(self):
  #   bass = {}
  #   for type in "root", "chord":
  #     center = self.notes[0]["center"]
  #     color1 = COLORS[type]
  #     color2 = "#000000"
  #     innerRadius = self.bassNoteRadius
  #     outerRadius = innerRadius + self.bassOutlinePlayedWidth
  #     rings = []
  #     numRings = outerRadius - innerRadius
  #     (r1,g1,b1) = self.winfo_rgb(color1)
  #     (r2,g2,b2) = self.winfo_rgb(color2)
  #     rStep = float(r2-r1) / numRings
  #     gStep = float(g2-g1) / numRings
  #     bStep = float(b2-b1) / numRings
  #     for i in range(0, numRings):
  #       r = innerRadius + i
  #       nr = int(r1 + (rStep * i))
  #       ng = int(g1 + (gStep * i))
  #       nb = int(b1 + (bStep * i))
  #       color = "#%4.4x%4.4x%4.4x" % (nr,ng,nb)
  #       x0, x1 = center["x"] - r, center["x"] + r
  #       y0, y1 = center["y"] - r, center["y"] + r
  #       ring = self.create_oval(x0, y0, x1, y1, fill='', outline=color, width=1, state='hidden')
  #       rings.append(ring)
  #     bass[type] = rings
  #   return bass

  
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
        "center": { "x": x, "y": y }
      }
      notes.append(note)
    return notes

  # def hideBassPlayed(self):
  #   for type in "chord", "root":
  #     for ring in self.bassPlayed[type]:
  #       self.itemconfigure(ring, state='hidden')
  
  # def showBassPlayed(self, isRoot):
  #   type = "chord"
  #   if isRoot: type = "root"
  #   for ring in self.bassPlayed[type]:
  #     self.itemconfigure(ring, state='normal')

  # def setBassPlayedPosition(self, note, isRoot):
  #   type = "chord"
  #   if isRoot: type = "root"

  #   center = self.notes[note]["center"]
  #   innerRadius = self.bassNoteRadius
  #   outerRadius = innerRadius + self.bassOutlinePlayedWidth
  #   numRings = outerRadius - innerRadius
  #   for i in range(0, numRings):
  #     r = innerRadius + i
  #     x0, x1 = center["x"] - r, center["x"] + r
  #     y0, y1 = center["y"] - r, center["y"] + r
  #     self.coords(self.bassPlayed[type][i], x0, y0, x1, y1)


  # def setBassColor(self, color):
  #   self.itemconfigure(self.bass, outline=color, fill=color)

  def setBassOutlineColor(self, color):
    self.itemconfigure(self.bass, outline=color)

  # def setBassHollow(self):
  #   self.itemconfigure(self.bass, fill='')

  def setBassPositionAndRadius(self, note, radius):
    centerX = self.width / 2
    centerY = self.height - centerX
    theta = ((note*-2*math.pi) / 12) + (0.5*math.pi)
    x = centerX + (self.bassRadius*math.cos(theta))
    y = centerY - (self.bassRadius*math.sin(theta))
    x0, x1 = x - radius, x + radius
    y0, y1 = y - radius, y + radius
    self.coords(self.bass, x0, y0, x1, y1)


  def setBassWidth(self, width):
    self.itemconfigure(self.bass, width=width)

  # def setBassDash(self, dash):
  #   self.itemconfigure(self.bass, dash=dash)

  def setNoteColor(self, note, color):
    self.itemconfigure(self.notes[note]["id"], fill=color, outline=color)

  def setNoteOutlineColor(self, note, color):
    self.itemconfigure(self.notes[note]["id"], outline=color)

  def setNoteHollow(self, note):
    self.itemconfigure(self.notes[note]["id"], fill='')
  
  def setNoteRadius(self, note, radius):
    x = self.notes[note]["center"]["x"]
    y = self.notes[note]["center"]["y"]
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
      if self.scale.count(note) != 0:
        isRoot = note == self.root
        self.setNoteInScale(note, isRoot)
      else:
        self.setNoteNotInScale(note)

  def setChord(self, chordTypes, rootType):
    self.root = (rootType + (12-self.key)) % 12
    self.setScale(self.scale)
    chord = []
    for i in chordTypes:
      chord.append((i + (12-self.key)) % 12)
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