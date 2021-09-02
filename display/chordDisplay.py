import tkinter as tk
import math
from constants import *

class ChordDisplay(tk.Canvas):
  height = 330
  width = 300
  radius = 120
  noteRadius = 20

  scaleColor = "#4a4a4a"

  playedColor = "#ffffff"
  playedRootColor = "#00d9ff"

  shadowColor = "#858585"
  shadowRootColor = "#567e85"

  def __init__(self, master=None):
    super().__init__(master, width=self.width, height=self.height, highlightthickness=0, relief="flat", bg="#000000")
    self.master = master
    self.scale = [0, 2, 4, 5, 7, 9, 11]
    self.positions, self.notes = self.createNotes()
    self.pack(side="bottom", pady=20)
  
  def createNotes(self):
    positions = []
    notes = []
    centerX = self.width / 2
    centerY = self.height - centerX
    for i in range(0, 12):
      fill = ''
      if self.scale.count(i) != 0:
        fill = self.scaleColor
      theta = ((i*-2*math.pi) / 12) + (0.5*math.pi)
      x = centerX + (self.radius*math.cos(theta))
      y = centerY - (self.radius*math.sin(theta))
      x0, x1 = x - self.noteRadius, x + self.noteRadius
      y0, y1 = y - self.noteRadius, y + self.noteRadius
      positions.append((x, y))
      notes.append(self.create_oval(x0, y0, x1, y1, fill=fill))
    return positions, notes

  def setNoteColor(self, note, color):
    self.itemconfigure(self.notes[note], fill=color)

  def setKey(self, key):
    self.key = key

  def setScale(self, scale):
    self.scale = scale
    for i in range(0, 12):
      fill = ''
      if self.scale.count(i) != 0:
        fill = self.scaleColor
      self.setNoteColor(i, fill)

  def setChord(self, chordTypes, rootType):
    self.setScale(self.scale)
    self.root = (rootType + (12-self.key)) % 12
    chord = []
    for i in chordTypes:
      chord.append((i + (12-self.key)) % 12)
    self.chord = chord

  def setChordShadow(self):
    for note in self.chord:
      color = self.shadowColor
      if note == self.root:
        color = self.shadowRootColor
      self.setNoteColor(note, color)

  def playChord(self):
    for note in self.chord:
      color = self.playedColor
      if note == self.root:
        color = self.playedRootColor
      self.setNoteColor(note, color)