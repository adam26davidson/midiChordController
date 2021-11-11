from chord import Chord

def parseSecondaries(settings):
  def parseSecondary(setting):
    secondaries = {}
    default = Secondary(setting)
    buttons = ["south", "west", "north", "east"]
    def getOverrideSecondary(overides):
      overideSettings = setting.copy()
      for key in overides:
        overideSettings[key] = overides[key]
      return Secondary(overideSettings)

    for button in buttons:
      if not (button in setting):
        secondaries[button] = {"default": default,"leftModulation": default, "rightModulation": default}
      else:
        secondaries[button] = {}
        for key in "default", "leftModulation", "rightModulation":
          if key in setting[button]:
            secondaries[button][key] = getOverrideSecondary(setting[button][key])
          else:
            secondaries[button][key] = default
    return secondaries

  left = parseSecondary(settings["left"])
  right = parseSecondary(settings["right"])
  return {"left": left, "right": right}

class Secondary():
  def __init__(self, setting):
    self.interval = setting["interval"]
    self.main = setting["main"]
    self.mainBass = setting["mainBass"]
    self.alt = setting["alternate"]
    self.altBass = setting["alternateBass"]

    # find actual notes and all midi notes for each key
    self.mainNotes, self.allMainNotes = self.findNotes(self.main)
    self.altNotes, self.allAltNotes = self.findNotes(self.alt)
    self.mainBassNotes, self.allMainBassNotes, self.mainBassRoots = self.findBassNotes(self.mainBass)
    self.altBassNotes, self.allAltBassNotes, self.altBassRoots = self.findBassNotes(self.altBass)

    self.mainVoicings = Chord.findVoicings(self.allMainNotes, len(self.main))
    self.altVoicings = Chord.findVoicings(self.allAltNotes, len(self.alt))

    # find the home inversion, number of top and bottom inversions
    self.mainInversionParams = Chord.findInversionParams(self.mainVoicings, len(self.main))
    self.altInversionParams = Chord.findInversionParams(self.altVoicings, len(self.alt))
    self.mainBassParams = Chord.findBassParams(self.allMainBassNotes, self.mainBassRoots)
    self.altBassParams = Chord.findBassParams(self.allAltBassNotes, self.altBassRoots)

  def findNotes(self, chord):
    notes = {}
    allNotes = {}
    for key in range(0, 12):
      notes[key] = []
      for note in chord:
        notes[key].append((note + key) % 12)
      notes[key].sort()
      allNotes[key] = Chord.findAllNotes(notes[key])
    return notes, allNotes

  def findBassNotes(self, notes):
    roots = {}
    for key in range(0, 12):
      roots[key] = (notes[0] + key) % 12
    notes, allNotes = self.findNotes(notes)
    return notes, allNotes, roots

  def getBassFromParams(self, midiShock, key, params, allNotes):
    root = (key + self.interval) % 12
    p = midiShock.bassPosition
    if p <= params[root]["topCount"] and p >= (-1*params[root]["bottomCount"]):
      return allNotes[root][params[root]["center"] + p]
    elif p > params[root]["topCount"]:
      return allNotes[root][len(allNotes[root]) - 1]
    elif p < (-1*params[root]["bottomCount"]):
      return allNotes[root][0]

  def getChordFromParams(self, midiShock, key, inversionParams, voicings):
    root = (key + self.interval) % 12
    spread = Chord.convertSpread(midiShock.spread, len(voicings[root][0][0]))
    if spread >= len(voicings[root]):
      spread = len(voicings[root]) - 1
    params = inversionParams[root][spread]
    # if the inversion is within range
    if midiShock.inversion <= params["topCount"] and midiShock.inversion >= (-1*params["bottomCount"]):
      return voicings[root][spread][params["center"] + midiShock.inversion]
    # if the inversion is above the range
    elif midiShock.inversion > params["topCount"]:
      # if upper limit is not exceeded by more than the spread
      if midiShock.inversion - params["topCount"] < spread:
        spreadVoicings = voicings[root][spread - (midiShock.inversion - params["topCount"])]
        return spreadVoicings[len(spreadVoicings)-1]
      # if upper limit is exceeded by more than the spread
      else:
        return voicings[root][0][len(voicings[root][0]) - 1]
    # if the inversion is below the lower limit
    elif midiShock.inversion < (-1*params["bottomCount"]):
      # if lower limit is not exceeded by more than the spread
      if midiShock.inversion + params["bottomCount"] < spread:
        spreadVoicings = voicings[root][spread - (midiShock.inversion + params["bottomCount"])]
        return spreadVoicings[0]
      # if the limit range is exceeded by more than the spread
      else:
        return voicings[root][0][0]

  def getRoot(self, key):
    return (key + self.interval) % 12

  def getNoteTypes(self, midiShock, key):
    root =  self.getRoot(key)
    if midiShock.alternate:
      return self.altNotes[root]
    else:
      return self.mainNotes[root]

  def getChord(self, midiShock, key):
    if midiShock.alternate:
      return self.getChordFromParams(midiShock, key, self.altInversionParams, self.altVoicings)
    else:
      return self.getChordFromParams(midiShock, key, self.mainInversionParams, self.mainVoicings)

  def getBass(self, midiShock, key):
    if midiShock.alternate:
      return self.getBassFromParams(midiShock, key, self.altBassParams, self.allAltBassNotes)
    else:
      return self.getBassFromParams(midiShock, key, self.mainBassParams, self.allMainBassNotes)