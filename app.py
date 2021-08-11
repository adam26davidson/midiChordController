import chord.Chord as Chord

class App:
  def __init__(self) {
    self.bottomNote = 21,
    self.topNote = 108
    self.currentSetting = 0
    self.rootKey = 0 # 0 is C
    self.inversion = 0
    self.spread = 11
    self.maxSpread = 60
    self.centerNote = 60 #bottom of base chord range

    self.settings = json.load("settings.json")[self.currentSetting]
    self.scale = self.settings["scale"]
    self.setScaleNotes()
    
  }

  def findAllNotes(self, notes, min=self.bottomNote, max=self.topNote) {
    completedNotes = []
    let midiNotes = []
    for note in notes:
      # ensure no duplicates
      if completedNotes.count(note) == 0:
        for i in range(min, max):
          if i % 12 == note:
            midiNotes.append(i)
        completedNotes.append(note)

    return midiNotes.sort()
  }

  def setScaleNotes(self):
    let scaleNotes = []
    for note in self.settings["scale"]:
      scaleNotes.append((note + self.rootKey) % 12)
    
    self.scaleNotes = scaleNotes
    


  def allScaleNotes(self) :
    return self.findAllNotes(self.scaleNotes)
  
      