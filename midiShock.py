from chord import Chord
from modulation import Modulation
from secondary import parseSecondaries, Secondary
from constants import *
import rtmidi 


class MidiShock:
  def __init__(self, settingIndex=0):

    # constant for each setting
    self.settingIndex = settingIndex
    self.setting = SETTINGS[settingIndex]
    self.midiOut = rtmidi.MidiOut()
    availablePorts = self.midiOut.get_ports()
    print(availablePorts)

    if len(availablePorts) > 1:
      self.midiOut.open_port(1)
    else:
      self.midiOut.open_virtual_port("virtual output")


    self.scale = self.setting["scale"]
    self.scaleNotes, self.allScaleNotes = self.findScaleNotes()

    self.chords = {
      "ex": Chord(self.scale, self.setting["chords"]["ex"]),
      "square": Chord(self.scale, self.setting["chords"]["square"]),
      "triangle": Chord(self.scale, self.setting["chords"]["triangle"]),
      "circle": Chord(self.scale, self.setting["chords"]["circle"])
    }

    self.secondaries = parseSecondaries(self.setting["secondaries"])

    self.modulations = {
      "left": Modulation(self.scale, self.setting["modulations"]["left"]),
      "right": Modulation(self.scale, self.setting["modulations"]["right"])
    }

    #state variables
    self.key = 0 # 0 is C, 1 is C# etc
    self.inversionRange = 6
    self.bassRange = 4
    self.spread = 0
    self.shift = False

    self.inversion = 0 
    self.bassPosition = 0 
    self.modulation = "none" # can be "left", "none", or "right"
    self.secondary = "none" # can be "left", "none", or "right"
    self.alternate = False

    self.playingChordNotes = [] # chord notes that are currently playing
    self.chordIsPlaying = False
    self.playingBassNote = None # bass note that is currently playing
    self.BassIsPlaying = False
    self.activeChord = "ex"

    self.chordType, self.rootType = self.getChordType(self.activeChord)

  def connectDisplay(self, display):
    self.display = display

    chord = self.chords[self.activeChord]
    self.display.setKey(self.key)
    self.display.setScale(self.scale)
    self.display.setChord(chord.mainNotes[self.key], chord.rootNotes[self.key])
    self.display.setChordShadow(self.getChord(self.activeChord))
    self.display.setBassShadow(self.getBass())
    self.display.setInversionRange(self.inversionRange, self.inversion)
    self.display.setBassPositionRange(self.bassRange, self.bassPosition)

  def updateDisplay(self):
    self.display.root.update()

  def sendMidi(self, notes, off=False):
    type = 0x90
    vel = 122
    if off:
      type = 0x80
      vel = 0

    for note in notes:
      print([type, note, vel])
      self.midiOut.send_message([type, note, vel])

  def findScaleNotesForKey(self, key):
    scaleNotes = []
    for note in self.scale:
      scaleNotes.append((note + key) % 12)
    return scaleNotes

  def findScaleNotes(self):
    scaleNotes = {}
    allScaleNotes = {}
    for key in range(0, 12):
      scaleNotes[key] = self.findScaleNotesForKey(key)
      allScaleNotes[key] = Chord.findAllNotes(scaleNotes[key])
    return scaleNotes, allScaleNotes

  def getScale(self):
    return self.scaleNotes[self.key]

  def mod12(self, notes):
    newNotes = []
    for note in notes:
      newNotes.append(note % 12)
    return newNotes

  def getChordType(self, button):
    chord = self.chords[button]
    # secondary inactive
    if (self.secondary == "none"):
      if (self.modulation == "none"):
        return chord.getNoteTypes(self), chord.getRoot(self)
      else:
        modulation = self.modulations[self.modulation]
        rootNote = modulation.applyOne(chord.getRoot(self), self) % 12
        chordNotes = self.mod12(modulation.apply(chord.getNoteTypes(self), self))
        return chordNotes, rootNote
    # secondary is active
    else:
      modKey = "default"
      if (self.modulation == "left"):
        modKey = "leftModulation"
      elif (self.modulation == "left"):
        modKey = "rightModulation"
      secondary = self.secondaries[self.secondary][button][modKey]
      chordRoot = chord.getRoot(self)
      rootType = secondary.getRoot(chordRoot)
      chordType = secondary.getNoteTypes(self, chordRoot)
      chordType.sort()
      return chordType, rootType
  
  def getChord(self, button):
    chord = self.chords[button]
    # secondary inactive
    if (self.secondary == "none"):
      if (self.modulation == "none"):
        return chord.getChord(self)
      else:
        modulation = self.modulations[self.modulation]
        return modulation.apply(chord.getChord(self), self)
    # secondary is active
    else:
      modKey = "default"
      if (self.modulation == "left"):
        modKey = "leftModulation"
      elif (self.modulation == "left"):
        modKey = "rightModulation"
      secondary = self.secondaries[self.secondary][button][modKey]
      return secondary.getChord(self, chord.getRoot(self))
  
  def getBass(self):
    chord = self.chords[self.activeChord]
    if (self.secondary == "none"):
      if (self.modulation == "none"):
        return chord.getBass(self)
      else:
        modulation = self.modulations[self.modulation]
        return modulation.applyOne(chord.getBass(self), self)
    # secondary is active
    else:
      modKey = "default"
      if (self.modulation == "left"):
        modKey = "leftModulation"
      elif (self.modulation == "left"):
        modKey = "rightModulation"

      secondary = self.secondaries[self.secondary][self.activeChord][modKey]
      return secondary.getBass(self, chord.getRoot(self))

  def playChord(self, button):
    self.activeChord = button
    self.setChordType()
    self.stopChord()
    notes = self.getChord(button)

    self.sendMidi(notes)
    self.updateBass()
    self.display.playChord(notes)
    print("NOTES ON - " + str(notes))

    self.playingChordNotes = notes
    self.chordIsPlaying = True

  def playBass(self):
    self.stopBass()
    bassNote = self.getBass()

    # TODO send midi note on
    self.sendMidi([bassNote])
    self.display.playBass(bassNote)
    print("NOTE ON - " + str(bassNote))

    self.playingBassNote = bassNote
    self.BassIsPlaying = True

  def updateChord(self):
    if (self.chordIsPlaying):
      self.playChord(self.activeChord)
    else:
      notes = self.getChord(self.activeChord)
      self.display.setChordShadow(notes)

  def updateBass(self):
    if (self.BassIsPlaying):
      self.playBass()
    else:
      note = self.getBass()
      self.display.setBassShadow(note)

  def setChordType(self):
    chord, root = self.getChordType(self.activeChord)
    if chord != self.chordType or root != self.rootType:
      self.chordType, self.rootType = chord, root
      self.display.setChord(chord, root)

  def stopChord(self):
    if self.chordIsPlaying:
      # TODO send midi notes off for playing chord
      self.sendMidi(self.playingChordNotes, off=True)
      self.display.stopChord(self.playingChordNotes)
      print("NOTES OFF - " + str(self.playingChordNotes))
      self.playingChordNotes = []
      self.chordIsPlaying = False
  
  def stopBass(self):
    if self.BassIsPlaying:
      # TODO send midi note off for playing bass
      self.sendMidi([self.playingBassNote], off=True)
      self.display.stopBass(self.playingBassNote)
      print("NOTE OFF - " + str(self.playingBassNote))
      self.playingBassNote = None
      self.BassIsPlaying = False 

  def setModulation(self, side):
    if self.modulation != side:
      self.modulation = side
      self.setChordType()
      self.updateChord()
      self.updateBass()

  def setSecondary(self, side):
    if self.secondary != side:
      self.secondary = side
      self.setChordType()
      self.updateChord()
      self.updateBass()

  def setAlternate(self, alternate):
    if self.alternate != alternate:
      self.alternate = alternate
      self.setChordType()
      self.updateChord()
      self.updateBass()

  def setInversion(self, inversion):
    if inversion != self.inversion:
      if abs(inversion) <= self.inversionRange:
        self.inversion = inversion
      elif inversion < 0:
        self.inversion = -1*self.inversionRange
      elif inversion > 0:
        self.inversion = self.inversionRange
      self.updateChord()
      self.display.setInversion(self.inversion)
  
  def setInversionRange(self, range):
    if range <= MAX_INVERSION_RANGE and range >= 0:
      self.inversionRange = range
    elif range < 0:
      self.inversionRange = 0
    elif range > MAX_INVERSION_RANGE:
      self.inversionRange = MAX_INVERSION_RANGE

    if self.inversion > self.inversionRange:
      self.inversion = self.inversionRange
      self.updateChord()
    elif self.inversion < -1*self.inversionRange:
      self.inversion = -1*self.inversionRange
      self.updateChord()
    self.display.setInversionRange(self.inversionRange, self.inversion)
  
  def setBassPosition(self, position):
    if position != self.bassPosition:
      if abs(position) <= self.bassRange:
        self.bassPosition = position
      elif position < 0:
        self.bassPosition = -1*self.bassRange
      elif position > 0:
        self.bassPosition = self.bassRange
      self.updateBass()
      self.display.setBassPosition(self.bassPosition)

  def setBassRange(self, range):
    if range <= MAX_BASS_RANGE and range >= 0:
      self.bassRange = range
    elif range < 0:
      self.bassRange = 0
    elif range > MAX_BASS_RANGE:
      self.bassRange = MAX_BASS_RANGE

    if self.bassPosition > self.bassRange:
      self.bassPosition = self.bassRange
      self.updateBass()
    elif self.bassPosition < -1*self.bassRange:
      self.bassPosition = -1*self.bassRange
      self.updateBass()
    self.display.setBassPositionRange(self.bassRange, self.bassPosition)

  def setSpread(self, spread):
    if spread >= 0 and spread < SPREAD_STEPS_PER_OCTAVE * MAX_SPREAD_OCTAVES:
      self.spread = spread
    elif spread < 0:
      self.spread = 0
    elif spread >= SPREAD_STEPS_PER_OCTAVE * MAX_SPREAD_OCTAVES:
      self.spread = (SPREAD_STEPS_PER_OCTAVE * MAX_SPREAD_OCTAVES) - 1
    self.updateChord()
    self.display.setSpread(self.spread)
  
  def incrementSpread(self):
    self.setSpread(self.spread + 1)

  def decrementSpread(self):
    self.setSpread(self.spread - 1)

  def setKey(self, key):
    key = key % 12
    if self.key != key:
      self.key = key
      self.display.setKey(self.key)
      self.setChordType()
      self.updateChord()
      self.updateBass()

  def incrementKey(self):
    self.setKey(self.key + 1)

  def decrementKey(self):
    self.setKey(self.key + 11)

  def toggleShift(self):
    self.shift = not self.shift