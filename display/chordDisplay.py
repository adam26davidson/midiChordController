import tkinter as tk
import math
from constants import *

class ChordDisplay(tk.Canvas):
  height = 350
  width = 300
  radius = 120
  noteRadius = 19
  bassRadius = 22
  keyTextOffset = -60
  keyTextFontSize = 20

  noteNames = ["C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B"]

  keyTextColor = "#ffffff"
  scaleColor = "#333333"

  playedColor = "#ffffff"
  playedRootColor = "#00d9ff"

  shadowColor = "#858585"
  shadowRootColor = "#567e85"

  def __init__(self, master=None):
    super().__init__(master, width=self.width, height=self.height, highlightthickness=0, relief="flat", bg="#000000")
    self.master = master
    self.key = 0
    self.scale = [0, 2, 4, 5, 7, 9, 11]
    self.positions, self.notes = self.createNotes()
    self.keyText = self.createKeyText()
    self.pack(side="right", pady=(30, 0), padx=(0,80))

  def createKeyText(self):
    x = self.width / 2
    y = self.positions[0][1] + self.keyTextOffset
    gap = 10
    lineY0 = (y - (self.keyTextOffset)) - (self.noteRadius + gap)
    lineY1 = y + (self.keyTextFontSize/2) + gap
    self.create_line(x, lineY0, x, lineY1, fill=self.keyTextColor)
    return self.create_text(x, y, fill=self.keyTextColor, text=self.noteNames[self.key])
  
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
    self.itemconfigure(self.keyText, text=self.noteNames[self.key])

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