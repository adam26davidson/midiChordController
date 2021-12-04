from modules.chord import Chord
from modules.modulation import Modulation
from modules.secondary import parseSecondaries, Secondary
from constants import *
import math
from rtmidi import MidiOut
from rtmidi.midiconstants import *
import asyncio

class MidiController:
  def __init__(self, display = None, settingIndex=0):

    # constant for each setting
    self.display = display
    self.settingIndex = settingIndex
    self.setting = SETTINGS[settingIndex]

    self.midiOut = MidiOut()
    availablePorts = self.midiOut.get_ports()
    print(availablePorts)

    if len(availablePorts) > 1:
      self.midiOut.open_port(1)
    else:
      self.midiOut.open_virtual_port("virtual output")

    #state variables
    self.key = 0 # 0 is C, 1 is C# etc.
    self.inversionRange = 4
    self.bassRange = 4
    self.spread = 0
    self.octave = 0
    self.voices = 8
    self.shift = False
    self.alt = False
    self.hold = False
    self.home = False
    self.inversionHold = False
    self.controller = None
    # midi channel
    self.channel = 1

    self.inversion = 0 
    self.bassPosition = 0 
    self.bassPositionMode = "incremental" #can be "incremental" or "continuous"
    self.modulation = "none" # can be "left", "none", or "right"
    self.secondary = "none" # can be "left", "none", or "right"
    self.alternate = False

    self.playingChordNotes = [] # chord notes that are currently playing
    self.chordIsPlaying = False
    self.playingBassNote = None # bass note that is currently playing
    self.BassIsPlaying = False
    self.activeChord = "south"
    self.afterTouchValue = 0

    self.running = False

    self.setSetting(self.settingIndex)
    self.chordType, self.rootType = self.__getChordType(self.activeChord)

  def start(self):
    self.running = True
    asyncio.ensure_future(self.__midiLoop())

  def updateDisplay(self):
    if self.display: self.display.root.update()

  def incrementSetting(self):
    self.setSetting((self.settingIndex + 1) % len(SETTINGS))

  def decrementSetting(self):
    newIndex = self.settingIndex - 1
    if (newIndex < 0):
      newIndex = len(SETTINGS) - 1
    self.setSetting(newIndex)

  def setSetting(self, setting):
    if self.display:
      self.display.setSetting("Loading...")
      self.updateDisplay()
    self.stopChord(buttonUp=False)
    self.stopBass(buttonUp=False)
    self.settingIndex = setting
    self.setting = SETTINGS[setting]

    self.scale = self.setting["scale"]
    print(f"SETTING NAME: {self.setting['name']}")
    self.scaleNotes, self.allScaleNotes = self.__findScaleNotes()

    self.chords = {
      "south": Chord(self.scale, self.setting["chords"]["south"]),
      "west": Chord(self.scale, self.setting["chords"]["west"]),
      "north": Chord(self.scale, self.setting["chords"]["north"]),
      "east": Chord(self.scale, self.setting["chords"]["east"])
    }

    self.secondaries = parseSecondaries(self.setting["secondaries"])

    self.modulations = {
      "left": Modulation(self.scale, self.setting["modulations"]["left"]),
      "right": Modulation(self.scale, self.setting["modulations"]["right"])
    }

    chord = self.chords[self.activeChord]
    if self.display:
      self.display.setKey(self.key)
      self.display.setScale(self.scale)
      self.display.setChord(chord.mainNotes[self.key], chord.rootNotes[self.key])
      self.display.setChordShadow(self.__getChord(self.activeChord))
      self.display.setBassShadow(self.__getBass())
      self.display.setInversionRange(self.inversionRange, self.inversion)
      self.display.setBassPositionRange(self.bassRange, self.bassPosition)

    self.chordType, self.rootType = self.__getChordType(self.activeChord)

    if self.display: self.display.setSetting(self.setting["name"])

  def setAfterTouch(self, value):
    self.afterTouchValue = value

  def playChord(self, button):
    self.activeChord = button
    self.__setChordType()
    self.stopChord(buttonUp=False)
    notes = self.__getChord(button)
    self.__sendMidi(notes)
    self.__updateBass()
    if self.display: self.display.playChord(notes)
    # print("NOTES ON - " + str(notes))

    self.playingChordNotes = notes
    self.chordIsPlaying = True

  def __setNumVoices(self, chordNotes):
    return chordNotes[:self.voices] if self.voices < len(chordNotes) else chordNotes

  def __setOctave(self, chordNotes):
    return [note + (self.octave * 12) for note in chordNotes]

  def playBass(self):
    self.stopBass(buttonUp=False)
    bassNote = self.__getBass()

    # TODO send midi note on
    self.__sendMidi([bassNote])
    if self.display: self.display.playBass(bassNote)
    # print("NOTE ON - " + str(bassNote))

    self.playingBassNote = bassNote
    self.BassIsPlaying = True

  def stopChord(self, buttonUp=True):
    if not buttonUp or not self.hold:
      if self.chordIsPlaying:
        # TODO send midi notes off for playing chord
        self.__sendMidi(self.playingChordNotes, command = NOTE_OFF)
        if self.display: self.display.stopChord(self.playingChordNotes)
        #print("NOTES OFF - " + str(self.playingChordNotes))
        self.playingChordNotes = []
        self.chordIsPlaying = False
  
  def stopBass(self, buttonUp=True):
    if not buttonUp or not self.hold:
      if self.BassIsPlaying:
        # TODO send midi note off for playing bass
        self.__sendMidi([self.playingBassNote], command = NOTE_OFF)
        if self.display: self.display.stopBass(self.playingBassNote)
        #print("NOTE OFF - " + str(self.playingBassNote))
        self.playingBassNote = None
        self.BassIsPlaying = False 

  def setModulation(self, side):
    if self.modulation != side:
      if self.display: 
        if side != "none":
          self.display.startModulation(self.modulations[side].applyToScale())
        else:
          self.display.stopModulation()
      self.modulation = side
      self.__setChordType()
      self.__updateChord()
      self.__updateBass()

  def setSecondary(self, side):
    if self.secondary != side:
      self.secondary = side
      self.__setChordType()
      self.__updateChord()
      self.__updateBass()

  def setAlternate(self, alternate):
    if self.alternate != alternate:
      self.alternate = alternate
      self.__setChordType()
      self.__updateChord()
      self.__updateBass()

  def setInversion(self, inversion, rawValue):
    if (not self.inversionHold):
      if self.display: self.display.storeInversionThumb(rawValue)
      if inversion != self.inversion:
        if abs(inversion) <= self.inversionRange:
          self.inversion = inversion
        elif inversion < 0:
          self.inversion = -1*self.inversionRange
        elif inversion > 0:
          self.inversion = self.inversionRange
        self.__updateChord()
        if self.display: self.display.setInversion(self.inversion)
  
  def setInversionRange(self, range):
    if range <= MAX_INVERSION_RANGE and range >= 0:
      self.inversionRange = range
    elif range < 0:
      self.inversionRange = 0
    elif range > MAX_INVERSION_RANGE:
      self.inversionRange = MAX_INVERSION_RANGE

    if self.inversion > self.inversionRange:
      self.inversion = self.inversionRange
      self.__updateChord()
    elif self.inversion < -1*self.inversionRange:
      self.inversion = -1*self.inversionRange
      self.__updateChord()
    if self.display: self.display.setInversionRange(self.inversionRange, self.inversion)

  def incrementBassPosition(self):
    newPosition = self.bassPosition + 1
    if abs(newPosition) <= self.bassRange:
      thumb = self.__getIncrementalInversionThumbValue(newPosition)
      self.setBassPosition(newPosition, thumb)

  def decrementBassPosition(self):
    newPosition = self.bassPosition - 1
    if abs(newPosition) <= self.bassRange:
      thumb = self.__getIncrementalInversionThumbValue(newPosition)
      self.setBassPosition(newPosition, thumb)
    
  def setBassPosition(self, position, rawValue):
    if self.display: self.display.storeBassPositionThumb(rawValue)
    if position != self.bassPosition:
      if abs(position) <= self.bassRange:
        self.bassPosition = position
      elif position < 0:
        self.bassPosition = -1*self.bassRange
      elif position > 0:
        self.bassPosition = self.bassRange
      self.__updateBass()
      if self.display: self.display.setBassPosition(self.bassPosition)

  def setBassRange(self, range):
    if range <= MAX_BASS_RANGE and range >= 0:
      self.bassRange = range
    elif range < 0:
      self.bassRange = 0
    elif range > MAX_BASS_RANGE:
      self.bassRange = MAX_BASS_RANGE

    if self.bassPosition > self.bassRange:
      self.bassPosition = self.bassRange
      self.__updateBass()
    elif self.bassPosition < -1*self.bassRange:
      self.bassPosition = -1*self.bassRange
      self.__updateBass()
    if self.display: self.display.setBassPositionRange(self.bassRange, self.bassPosition)

  def setSpread(self, spread):
    if spread >= 0 and spread < SPREAD_STEPS_PER_OCTAVE * MAX_SPREAD_OCTAVES:
      self.spread = spread
    elif spread < 0:
      self.spread = 0
    elif spread >= SPREAD_STEPS_PER_OCTAVE * MAX_SPREAD_OCTAVES:
      self.spread = (SPREAD_STEPS_PER_OCTAVE * MAX_SPREAD_OCTAVES) - 1
    self.__updateChord()
    if self.display: self.display.setSpread(self.spread)
  
  def incrementSpread(self):
    self.setSpread(self.spread + 1)

  def decrementSpread(self):
    self.setSpread(self.spread - 1)

  def setKey(self, key):
    key = key % 12
    if self.key != key:
      self.key = key
      if self.display: self.display.setKey(self.key)
      self.__setChordType()
      self.__updateChord()
      self.__updateBass()

  def incrementKey(self):
    self.setKey(self.key + 1)

  def decrementKey(self):
    self.setKey(self.key + 11)
  
  def incrementVoices(self):
    self.voices = (self.voices % MAX_VOICING) + 1 if self.voices < MAX_VOICING else 2
  
  def decrementVoices(self):
    """Does not go less than 2 voices."""
    self.voices = ((MAX_VOICING + 1) if self.voices < 3 else self.voices) - 1
  
  def incrementMidiChannel(self):
    self.channel = (self.channel % 16) + 1
  
  def decrementMidiChannel(self):
    self.channel = (17 if self.channel < 2 else self.channel) - 1

  def incrementOctave(self):
    self.octave = self.octave + 1 if self.octave < 3 else self.octave
  
  def decrementOctave(self):
    self.octave = self.octave - 1 if self.octave > -3 else self.octave

  def toggleShift(self):
    self.shift = not self.shift
    if self.display: self.display.setShift(self.shift)

  def toggleAlt(self):
    self.alt = not self.alt
    if self.display: self.display.setAlt(self.alt)
  
  def toggleHold(self):
    if self.hold:
      self.hold = False
      self.stopChord(buttonUp=False)
      self.stopBass(buttonUp=False)
    else:
      self.hold = True
  
  def toggleInversionHold(self):
    self.inversionHold = not self.inversionHold

  def toggleHome(self):
    self.home = not self.home

  def processCCValue(self, rawValue, name, config):
    max = config["ranges"][name]["bottom"]
    value = math.floor((min(abs(rawValue), max) / max)*127)
    return value

  def processThresholdValue(self, rawValue, name, config):
    range = config["ranges"][name]
    center = abs((range["top"] - range["bottom"]) / 2)
    threshold = range["threshold"] * center
    if rawValue > (center + threshold):
      return 1
    if rawValue < (center - threshold):
      return -1
    else:
      return 0

  def processInversionValue(self, rawValue, name, config, pastValues, type="chord"):
    maxSteps = self.inversionRange
    if (type == "bass"):
      maxSteps = self.bassRange

    range = config["ranges"][name]

    pastRawValues = pastValues["past"]
    pastRawValues.append(rawValue)
    if (len(pastRawValues) > config["absAverageCounts"][name]):
      pastRawValues.pop(0)

    # get the average of the past raw values (prevents fluttering)
    sum = 0
    for val in pastRawValues:
      sum += val
    avg = sum / len(pastRawValues)

    #clamp value to between -0.999 and 0.999
    slope = 2.0 / (range["top"]- range["bottom"])
    intercept = 1 - (slope*range["top"])
    normalized =  (slope*avg) + intercept
    normalized = max(min(normalized, 0.999), -0.999)
    
    # converts to an integer in the correct inversion range
    def getValue(n):
      if n > 0:
        return math.floor(n * (maxSteps + 1))
      else:
        return math.ceil(n * (maxSteps + 1))

    # snap processed value back into current window if     
    snapped = normalized
    value = getValue(snapped)
    snap = (1.0 / (maxSteps + 1)) * INVERSION_SNAP

    if value == pastValues["processed"] + 1:
      snapped -= snap
      value = getValue(snapped)
    if value == pastValues["processed"] - 1:
      snapped += snap
      value = getValue(snapped)

    pastValues["processed"] = value
    return value, normalized
  
  async def __midiLoop(self):
    while(self.running):
      self.__sendAfterTouch()
      await asyncio.sleep(MIDI_STEP)

  def __getIncrementalInversionThumbValue(self, position):
    thumb = 0
    if position > 0:
      step = 1 / (self.bassRange + 1)
      thumb = (position + 0.5) * step
    elif position < 0:
      step = 1 / (self.bassRange + 1)
      thumb = (position - 0.5) * step
    return thumb

  def __sendAfterTouch(self):
    if(self.chordIsPlaying):
      for note in self.playingChordNotes:
        self.midiOut.send_message([0xA0, note, self.afterTouchValue])
    if self.BassIsPlaying:
      self.midiOut.send_message([0xA0, self.playingBassNote, self.afterTouchValue])

  def __findScaleNotesForKey(self, key):
    scaleNotes = []
    for note in self.scale:
      scaleNotes.append((note + key) % 12)
    return scaleNotes

  def __findScaleNotes(self):
    scaleNotes = {}
    allScaleNotes = {}
    for key in range(0, 12):
      scaleNotes[key] = self.__findScaleNotesForKey(key)
      allScaleNotes[key] = Chord.findAllNotes(scaleNotes[key])
    return scaleNotes, allScaleNotes
  
  def __sendMidi(self, notes, command = NOTE_ON, channel = None, velocity = 122):
    vel =  0 if command == NOTE_OFF else velocity
    midiCommandWithChannel = (command & 0xf0) | ((channel if channel else self.channel) - 1 & 0xf)
    for note in notes:
      self.midiOut.send_message([POLY_AFTERTOUCH, note, self.afterTouchValue])
      self.midiOut.send_message([midiCommandWithChannel, note, vel])
  
  def __mod12(self, notes):
    newNotes = []
    for note in notes:
      newNotes.append(note % 12)
    return newNotes

  def __getChordType(self, button):
    chord = self.chords[button]
    # secondary inactive
    if (self.secondary == "none"):
      if (self.modulation == "none"):
        return chord.getNoteTypes(self), chord.getRoot(self.key)
      else:
        modulation = self.modulations[self.modulation]
        rootNote = modulation.applyOne(chord.getRoot(self.key), self.__getScale()) % 12
        chordNotes = self.__mod12(modulation.apply(chord.getNoteTypes(self), self.__getScale()))
        return chordNotes, rootNote
    # secondary is active
    else:
      modKey = "default"
      if (self.modulation == "left"):
        modKey = "leftModulation"
      elif (self.modulation == "left"):
        modKey = "rightModulation"
      secondary = self.secondaries[self.secondary][button][modKey]
      chordRoot = chord.getRoot(self.key)
      rootType = secondary.getRoot(chordRoot)
      chordType = secondary.getNoteTypes(self, chordRoot)
      chordType.sort()
      return chordType, rootType

  def __setChordType(self):
    chord, root = self.__getChordType(self.activeChord)
    if chord != self.chordType or root != self.rootType:
      self.chordType, self.rootType = chord, root
      if self.display: self.display.setChord(chord, root)

  def __getChord(self, button):
    chord = self.chords[button]
    # secondary inactive
    if (self.secondary == "none"):
      if (self.modulation == "none"):
        chord = chord.getChord(self)
      else:
        modulation = self.modulations[self.modulation]
        chord = modulation.apply(chord.getChord(self), self.__getScale())
    # secondary is active
    else:
      modKey = "default"
      if (self.modulation == "left"):
        modKey = "leftModulation"
      elif (self.modulation == "left"):
        modKey = "rightModulation"
      secondary = self.secondaries[self.secondary][button][modKey]
      chord = secondary.getChord(self, chord.getRoot(self.key))
    
    chordAdjustedNumVoices = self.__setNumVoices(chord)
    chordAdjustedOctaves = self.__setOctave(chordAdjustedNumVoices)
    return chordAdjustedOctaves

  def __setNumVoices(self, chordNotes):
    return chordNotes[:self.voices] if self.voices < len(chordNotes) else chordNotes

  def __setOctave(self, chordNotes):
    return [note + (self.octave * 12) for note in chordNotes]
 
  def __getScale(self):
    return self.scaleNotes[self.key]
  
  def __getBass(self):
    chord = self.chords[self.activeChord]
    if (self.secondary == "none"):
      if (self.modulation == "none"):
        return chord.getBass(self)
      else:
        modulation = self.modulations[self.modulation]
        return modulation.applyOne(chord.getBass(self), self.__getScale())
    # secondary is active
    else:
      modKey = "default"
      if (self.modulation == "left"):
        modKey = "leftModulation"
      elif (self.modulation == "left"):
        modKey = "rightModulation"

      secondary = self.secondaries[self.secondary][self.activeChord][modKey]
      return secondary.getBass(self, chord.getRoot(self.key))

  def __updateChord(self):
    if (self.chordIsPlaying):
      self.playChord(self.activeChord)
    else:
      notes = self.__getChord(self.activeChord)
      if self.display: self.display.setChordShadow(notes)

  def __updateBass(self):
    if (self.BassIsPlaying):
      self.playBass()
    else:
      note = self.__getBass()
      if self.display: self.display.setBassShadow(note)