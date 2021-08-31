from display.keyboard import Keyboard

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
    self.shadowBassNote = 48

    self.keyboard = Keyboard(master=self.root)

  def stopChordShadow(self):
    resetNotes = []
    for note in self.shadowChordNotes:
      if note != self.shadowBassNote:
        resetNotes.append(note)
    self.keyboard.reset(resetNotes)
    self.shadowChordNotes = []

  def stopBassShadow(self):
    if self.shadowChordNotes.count(self.shadowBassNote) == 0:
      self.keyboard.reset([self.shadowBassNote])
    self.shadowBassNote = None

  def setChord(self, chord, root):
    self.keyboard.setChord(chord, root)
  
  def playChord(self, notes):
    self.stopChordShadow()
    self.keyboard.play(notes)
  
  def playBass(self, note):
    self.stopBassShadow()
    self.keyboard.play([note])

  def stopChord(self, notes):
    self.shadowChordNotes = notes
    self.keyboard.setShadow(notes)

  def stopBass(self, note):
    self.shadowBassNote = note
    self.keyboard.setShadow([note])

  def setChordShadow(self, notes):
    self.keyboard.reset(self.shadowChordNotes)
    self.shadowChordNotes = notes
    self.keyboard.setShadow(notes)

  def setBassShadow(self, note):
    self.keyboard.reset([self.shadowBassNote])
    self.shadowBassNote = note
    self.keyboard.setShadow([note])
