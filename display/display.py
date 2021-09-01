from display.keyboard import Keyboard
from display.inversion import Inversion

class Display():
  def __init__(self, root):
    self.height = 480
    self.width = 800
    self.root = root

    root.overrideredirect(True)
    root.overrideredirect(False)

    root.attributes("-fullscreen", True)
    root.wm_attributes("-topmost", 1)
    root.focus_set()

    def close_escape(event=None):
      print("escaped")
      root.destroy()

    root.bind("<Escape>", close_escape)

    #self.root.geometry("800x480")
    self.root.configure(bg='black')
    self.root.attributes("-fullscreen", True)

    self.shadowChordNotes = []
    self.playingChordNotes = []
    self.shadowBassNote = 48
    self.playingBassNote = None

    self.keyboard = Keyboard(master=self.root)
    self.inversion = Inversion(master=self.root)

  def setInversionRange(self, range, inversion):
    self.inversion.setMax(range, inversion)
  
  def setInversion(self, inversion):
    self.inversion.setActiveRegion(inversion)

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
  
  def playChord(self, notes):
    self.stopChordShadow()
    self.keyboard.play(notes)
    self.playingChordNotes = notes
  
  def playBass(self, note):
    self.stopBassShadow()
    self.keyboard.play([note])
    self.playingBassNote = note

  def stopChord(self, notes):
    self.shadowChordNotes = notes
    self.keyboard.setShadow(notes)
    self.playingChordNotes = []

  def stopBass(self, note):
    if self.playingChordNotes.count(note) == 0:
      self.keyboard.setShadow([note])
    self.shadowBassNote = note
    self.playingBassNote = None

  def setChordShadow(self, notes):
    self.keyboard.reset(self.shadowChordNotes)
    self.shadowChordNotes = notes
    self.keyboard.setShadow(notes)

  def setBassShadow(self, note):
    self.stopBassShadow()
    self.shadowBassNote = note
    noteInPlayingChord = self.playingChordNotes.count(note) != 0
    if not noteInPlayingChord:
      self.keyboard.setShadow([note])
