from constants import *
from .chordDisplay import ChordDisplay
from .keyboard import Keyboard
from .inversion import Inversion
from .spread import Spread
from .textDisplay import TextDisplay
import asyncio
import tkinter as tk

class Display():
  def __init__(self):
    self.height = 480
    self.width = 800
    self.root = tk.Tk()

    self.root.overrideredirect(True)
    self.root.overrideredirect(False)

    if FULLSCREEN:
      self.root.attributes("-fullscreen", True)
      self.root.wm_attributes("-topmost", 1)
      self.root.focus_set()
    else:
      self.root.geometry("800x480")

    def close_escape(event=None):
      print("escaped")
      self.root.destroy()

    self.root.bind("<Escape>", close_escape)


    self.root.configure(bg='black')

    self.shadowChordNotes = []
    self.playingChordNotes = []
    self.shadowBassNote = 48
    self.playingBassNote = None
    self.inversionThumbValue = 0
    self.bassThumbValue = 0

    self.keyboard = Keyboard(master=self.root)
    self.spread = Spread(master=self.root)
    self.inversion = Inversion(master=self.root)
    self.bassPosition = Inversion(master=self.root)
    self.chordDisplay = ChordDisplay(master=self.root)
    self.textDisplay = TextDisplay(master=self.root)

  async def mainLoop(self):
    while True:
      self.setInversionThumb()
      self.setBassPositionThumb()
      self.chordDisplay.runAnimationStep()
      self.root.update()
      await asyncio.sleep(ANIMATION_STEP)
  
  def setController(self, text):
    self.textDisplay.setController(text)

  def setSetting(self, text):
    self.textDisplay.setSetting(text)

  def setAlt(self, alt):
    self.textDisplay.setAlt(alt)

  def setShift(self, shift):
    self.textDisplay.setShift(shift)
  
  def setKey(self, key):
    self.chordDisplay.setKey(key)

  def setScale(self, scale):
    self.chordDisplay.setScale(scale)

  def setInversionRange(self, range, inversion):
    self.inversion.setMax(range, inversion)
  
  def setInversion(self, inversion):
    self.inversion.setActiveRegion(inversion)

  def storeInversionThumb(self, value):
    self.inversionThumbValue = value

  def setInversionThumb(self):
    self.inversion.positionThumb(self.inversionThumbValue)

  def setBassPositionRange(self, range, position):
    self.bassPosition.setMax(range, position)
  
  def setBassPosition(self, position):
    self.bassPosition.setActiveRegion(position)

  def storeBassPositionThumb(self, value):
    self.bassThumbValue = value

  def setBassPositionThumb(self):
    self.bassPosition.positionThumb(self.bassThumbValue)
  
  def setSpread(self, spread):
    self.spread.setValue(spread)

  def stopChordShadow(self):
    resetNotes = []
    for note in self.shadowChordNotes:
      if note != self.shadowBassNote:
        resetNotes.append(note)
    self.keyboard.reset(resetNotes)
    self.shadowChordNotes = []

  def stopBassShadow(self):
    noteInPlayingChord = self.playingChordNotes.count(self.shadowBassNote) != 0
    noteInShadowChord = self.shadowChordNotes.count(self.shadowBassNote) != 0
    if (not noteInPlayingChord) and (not noteInShadowChord):
      self.keyboard.reset([self.shadowBassNote])
    self.shadowBassNote = None

  def setChord(self, chord, root):
    self.keyboard.setChord(chord, root)
    self.chordDisplay.setChord(chord, root)
  
  def playChord(self, notes):
    self.stopChordShadow()
    self.keyboard.play(notes)
    self.playingChordNotes = notes
    self.chordDisplay.playChord()
  
  def playBass(self, note):
    self.stopBassShadow()
    self.keyboard.play([note])
    self.chordDisplay.playBass(note)
    self.playingBassNote = note

  def stopChord(self, notes):
    self.shadowChordNotes = notes
    self.keyboard.setShadow(notes)
    self.playingChordNotes = []
    self.chordDisplay.setChordShadow()

  def stopBass(self, note):
    if self.playingChordNotes.count(note) == 0:
      self.keyboard.setShadow([note])
    self.chordDisplay.setBassShadow(note)
    self.shadowBassNote = note
    self.playingBassNote = None

  def setChordShadow(self, notes):
    self.keyboard.reset(self.shadowChordNotes)
    self.shadowChordNotes = notes
    self.keyboard.setShadow(notes)
    self.chordDisplay.setChordShadow()

  def setBassShadow(self, note):
    self.stopBassShadow()
    self.shadowBassNote = note
    noteInPlayingChord = self.playingChordNotes.count(note) != 0
    if not noteInPlayingChord:
      self.keyboard.setShadow([note])
    self.chordDisplay.setBassShadow(note)

  def startModulation(self, map):
    self.chordDisplay.startModulation(map)
  
  def stopModulation(self):
    pass
    #self.chordDisplay.stopModulation()
