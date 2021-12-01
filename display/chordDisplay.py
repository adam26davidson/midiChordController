import tkinter as tk
import math
from constants import *
from .displayConstants import COLORS, FONTS

class ChordDisplay(tk.Canvas):
  height = 350
  width = 300
  radius = 120

  smallNoteRadius = 13
  largeNoteRadius = 18
  outlineWidth = 3

  bassRadius = 22
  bassDash = (5, 5)
  bassOutlineShadowWidth = 3
  bassOutlinePlayedWidth = 5

  keyTextOffset = -60
  keyTextFontSize = 30

  noteNames = ["C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B"]

  def __init__(self, master=None):
    super().__init__(master, width=self.width, height=self.height, highlightthickness=0, relief="flat", bg="#000000")
    self.master = master
    self.key = 0
    self.root = 0
    self.scale = [0, 2, 4, 5, 7, 9, 11]
    self.notes = self.createNotes()
    self.keyText = self.createKeyText()
    self.pack(side="right", pady=(30, 0), padx=(0,80))

  def createKeyText(self):
    x = self.width / 2
    y = self.notes[0]["center"]["y"] + self.keyTextOffset
    return self.create_text(x, y, fill=COLORS["chord"], text=self.noteNames[self.key], font=FONTS["big"])

  def createBassNote(self):
    center = self.notes[0]["center"]
    x0, x1 = center["x"] - self.bassRadius, center["x"] + self.bassRadius
    y0, y1 = center["y"] - self.bassRadius, center["y"] + self.bassRadius
    bassNote = self.create_oval(x0, y0, x1, y1, 
      fill='', 
      outline=COLORS["root"], 
      dash=self.bassDash, 
      width=self.bassOutlineShadowWidth
    )
  
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