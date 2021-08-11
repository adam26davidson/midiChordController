class Chord:
  def __init__(self, app, chord):
    self.root = chord["root"] # index of the root in key agnostic scale

    self.rootNote = (app.scale[chord["root"]] + app.rootKey) % 12 # actual root
    self.main = chord["main"]
    self.alt = chord["alternate"]
    self.setNotes(app, chord)

  def setNotes(self, app, chord):
    #set main chord notes
    mainNotes = []
    for note in chord["main"]:
      index = (note + chord["root"]) % len(app.scale)
      mainNotes.append((app.scale[index] + app.rootKey) % 12)
    self.mainNotes = mainNotes
    self.allMainNotes = app.findAllNotes(notes)
    
    #set alternate chord notes
    altNotes = []
    for note in chord["alternate"]:
      index = (note + chord["root"]) % len(app.scale)
      altNotes.append((app.scale[index] + app.rootKey) % 12)
    self.altNotes = altNotes
    self.allAltNotes = app.findAllNotes(altNotes)
