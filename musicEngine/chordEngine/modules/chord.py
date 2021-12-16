from constants import *

class Chord:
  def __init__(self, scale, setting):

    self.scale = scale # set scale for convenience
    self.root = setting["root"] # index of the root in key agnostic scale

    self.main = setting["main"] # indices of chord notes in key agnostic scale
    self.mainBass = setting["mainBass"] # indices of alternate chord notes in key agnostic scale
    self.alt = setting["alternate"] # indices of alternate chord notes in key agnostic scale
    self.altBass = setting["alternateBass"] # indices of alternate chord notes in key agnostic scale

    self.rootNotes = self.findRootNotes() # set root note for each key

    # find chord and bass notes for each key 
    self.mainNotes, self.allMainNotes = self.findNotes(self.main)
    self.altNotes, self.allAltNotes = self.findNotes(self.alt)
    self.mainBassNotes, self.allMainBassNotes, self.mainBassRoots = self.findBassNotes(self.mainBass)
    self.altBassNotes, self.allAltBassNotes, self.altBassRoots = self.findBassNotes(self.altBass)

    # find all the voicings for each chord and spread value
    self.mainVoicings = Chord.findVoicings(self.allMainNotes, len(self.main))
    self.altVoicings = Chord.findVoicings(self.allAltNotes, len(self.alt))

    # find the home inversion, number of top and bottom inversions
    self.mainInversionParams = Chord.findInversionParams(self.mainVoicings, len(self.main))
    self.altInversionParams = Chord.findInversionParams(self.altVoicings, len(self.alt))
    self.mainBassParams = Chord.findBassParams(self.allMainBassNotes, self.mainBassRoots)
    self.altBassParams = Chord.findBassParams(self.allAltBassNotes, self.altBassRoots)

  #find all octaves of the specified array of notes
  def findAllNotes(notes, min=MIN_NOTE, max=MAX_NOTE):
    completedNotes = []
    midiNotes = []
    for note in notes:
      # ensure no duplicates
      if completedNotes.count(note) == 0:
        for i in range(min, max + 1):
          if i % 12 == note:
            midiNotes.append(i)
        completedNotes.append(note)
    midiNotes.sort()
    return midiNotes

  # set the root of the chord for each key
  def findRootNotes(self):
    rootNotes = {}
    for key in range(0, 12):
      rootNotes[key] = (self.scale[self.root] + key) % 12
    return rootNotes

  def findNotes(self, chord):
    #set main chord notes
    notes = {}
    allNotes = {}
    for key in range(0, 12):
      keyNotes = []
      for note in chord:
        index = (note + self.root) % len(self.scale)
        keyNotes.append((self.scale[index] + key) % 12)
        keyNotes.sort()
      notes[key] = keyNotes # chord notes for key
      allNotes[key] = Chord.findAllNotes(keyNotes) # all octaves of chord notes for key
    return notes, allNotes

  def findBassNotes(self, degrees):
    roots = {}
    for key in range(0, 12):
      index = (degrees[0] + self.root) % len(self.scale)
      roots[key] = (self.scale[index] + key) % 12
    notes, allNotes = self.findNotes(degrees)
    return notes, allNotes, roots

  def findVoicings(allChordNotes, n):
    vps = VOICING_PATTERNS[str(n)]
    voicings = {}
    # find all voicings for each key for each spread
    for key in range(0, 12):
      voicings[key] = []
      # for each spread s, find all the voicings in range for key
      for s in range(0, len(vps)):
        offset = 0
        top = vps[s][n-1]
        spreadVoicings = []
        # get all the valid positions of the spread pattern in the note range
        while top < len(allChordNotes[key]): 
          voicing = []
          for i in range(0, n):
            voicing.append(allChordNotes[key][offset + vps[s][i]])
          spreadVoicings.append(voicing)
          offset += 1
          top = vps[s][n-1] + offset
        voicings[key].append(spreadVoicings)
    return voicings

  def findInversionParams(voicings, n):
    inversionParams = {}
    # for each key k
    for k in range(0, 12):
      inversionParams[k] = {}
      # for each spread s
      for s in range(0, len(voicings[k])):
        inversionParams[k][s] = {}
        minScore = 1000000
        homePosition = 0
        # for each inversion position p
        for p in range(0, len(voicings[k][s])):
          score = (((voicings[k][s][p][n-1] + voicings[k][s][p][0]) / 2.0) - CENTER_NOTE) ** 2
          if score < minScore:
            minScore = score
            homePosition = p
        inversionParams[k][s] = {
          "center": homePosition, 
          "topCount": (len(voicings[k][s]) - homePosition) - 1,
          "bottomCount": homePosition
          }
      
    return inversionParams

  def findBassParams(allNotes, roots):
    params = {}
    for k in range(0, 12):
      params[k] = {}
      for n in range(0, len(allNotes[k])):
        inRange = allNotes[k][n] >=BASS_OCTAVE_RANGE["min"] and allNotes[k][n] <= BASS_OCTAVE_RANGE["max"]
        isRoot = allNotes[k][n] % 12 == roots[k]
        if inRange and isRoot:
          params[k] = {
            "center": n,
            "topCount": (len(allNotes[k]) - n) - 1,
            "bottomCount": n
          }
          break
    return params

  def convertSpread(spread, chordLength):
    spreadsPerOct = chordLength - 1
    spreadOctaves = (spread * (1 / SPREAD_STEPS_PER_OCTAVE))
    return int(spreadOctaves*spreadsPerOct)

  def getBassFromParams(self, state, params, allNotes):
    p = state['bassPosition']
    key = state['key']
    if p <= params[key]["topCount"] and p >= (-1*params[key]["bottomCount"]):
      return allNotes[key][params[key]["center"] + p]
    elif p > params[key]["topCount"]:
      return allNotes[key][len(allNotes[key]) - 1]
    elif p < (-1*params[key]["bottomCount"]):
      return allNotes[key][0]

  def getChordFromParams(self, state, inversionParams, voicings):
    keyVoicings = voicings[state['key']]
    spread = Chord.convertSpread(state['spread'], len(keyVoicings[0][0]))
    # ensure that spread is within range
    if spread >= len(keyVoicings):
      spread = len(keyVoicings) - 1
    params = inversionParams[state['key']][spread]
    # if the inversion is within range
    if state['inversion'] <= params["topCount"] and state['inversion'] >= (-1*params["bottomCount"]):
      return keyVoicings[spread][params["center"] + state['inversion']]
    # if the inversion is above the range
    elif state['inversion'] > params["topCount"]:
      # if upper limit is not exceeded by more than the spread
      if state['inversion'] - params["topCount"] < spread:
        spreadVoicings = keyVoicings[spread - (state['inversion'] - params["topCount"])]
        return spreadVoicings[len(spreadVoicings)-1]
      # if upper limit is exceeded by more than the spread
      else:
        return keyVoicings[0][len(keyVoicings[0]) - 1]
    # if the inversion is below the lower limit
    elif state['inversion'] < (-1*params["bottomCount"]):
      # if lower limit is not exceeded by more than the spread
      if ((-1*params["bottomCount"]) - state['inversion']) < spread:
        spreadVoicings = keyVoicings[spread - ((-1*params["bottomCount"]) - state['inversion'])]
        return spreadVoicings[0]
      # if the limit range is exceeded by more than the spread
      else:
        return keyVoicings[0][0]

  def getRoot(self, key):
    return self.rootNotes[key]

  def getNoteTypes(self, state):
    if state['alternate']:
      return self.altNotes[state['key']]
    else:
      return self.mainNotes[state['key']]

  def getChord(self, state):
    if state['alternate']:
      return self.getChordFromParams(state, self.altInversionParams, self.altVoicings)
    else:
      return self.getChordFromParams(state, self.mainInversionParams, self.mainVoicings)

  def getBass(self, state):
    if state['alternate']:
      return self.getBassFromParams(state, self.altBassParams, self.allAltBassNotes)
    else:
      return self.getBassFromParams(state, self.mainBassParams, self.allMainBassNotes)
