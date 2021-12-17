from .modules.chord import Chord
from .modules.modulation import Modulation
from .modules.secondary import parseSecondaries
from constants import *
from redux import store
from redux.actions import musicEngine as actions
import math, asyncio

class ChordEngine:
  def __init__(self, settingIndex=0):

    self.setting = SETTINGS[settingIndex]
    settingsList = [s['name'] for s in SETTINGS]
    store.dispatch(actions.changeSettingsList(settingsList))
    self.callbacks = []
    self.state = {
      'settingIndex': settingIndex,
      'loadingSetting': False,

      'scale': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
      'scaleNotes': [],
      'allScaleNotes': [],

      'key': 0, # 0 is C, 1 is C# etc.
      'inversionRange': 4,
      'inversionMode': 'incremental', #can be "incremental" or "continuous"
      'bassRange': 4,
      'bassMode': 'incremental', #can be "incremental" or "continuous"
      'inversion': 0,
      'bassPosition': 0,
      'chordOctave': 0,
      'spread': 0,

      'voiceCount': 16,
      'voiceCountMode': 'max', # can be 'max' or 'absolute'
      'hold': False,
      'inversionLock': False,

      'modulation': 'none', # can be "left", "none", or "right"
      'secondary': 'none', # can be "left", "none", or "right"
      'alternate': False,

      'rootType': 0,
      'chordType': [],
      'playingChordNotes': [],
      'chordIsPlaying': False,
      'playingBassNote': None,
      'bassIsPlaying': False,
      'activeChord': 'south',
    }

    store.dispatch(actions.changeKey(self.state['key']))
    store.dispatch(actions.changeInversionRange(self.state['inversionRange']))
    store.dispatch(actions.changeBassRange(self.state['bassRange']))
    store.dispatch(actions.changeInversion(self.state['inversion']))
    store.dispatch(actions.changeBassPosition(self.state['bassPosition']))

    self.setSetting(self.state['settingIndex'])


  def incrementSetting(self):
    self.setSetting((self.state['settingIndex'] + 1) % len(SETTINGS))

  def decrementSetting(self):
    newIndex = self.state['settingIndex'] - 1
    if (newIndex < 0):
      newIndex = len(SETTINGS) - 1
    self.setSetting(newIndex)

  def setSetting(self, setting):
    self.state['loadingSetting'] = True
    store.dispatch(actions.changeSettingLoading(True))
    self.stopChord(buttonUp=False)
    self.stopBass(buttonUp=False)
    self.state['settingIndex'] = setting
    self.setting = SETTINGS[setting]

    scale = self.setting["scale"]
    self.state['scale'] = scale
    self.state['scaleNotes'], self.state['allScaleNotes'] = self.__findScaleNotes()

    self.chords = {
      "south": Chord(scale, self.setting["chords"]["south"]),
      "west": Chord(scale, self.setting["chords"]["west"]),
      "north": Chord(scale, self.setting["chords"]["north"]),
      "east": Chord(scale, self.setting["chords"]["east"])
    }

    self.secondaries = parseSecondaries(self.setting["secondaries"])

    self.modulations = {
      "left": Modulation(scale, self.setting["modulations"]["left"]),
      "right": Modulation(scale, self.setting["modulations"]["right"])
    }

    types = self.__getChordType(self.state['activeChord'])
    self.state['chordType'], self.state['rootType'] = types


    store.dispatch(actions.changeSetting(setting))
    store.dispatch(actions.changeScale(scale))
    store.dispatch(actions.changeChordType({
      'chord': self.state['chordType'], 
      'root': self.state['rootType']
    }))
    shadowChord = self.__getChord(self.state['activeChord'])
    store.dispatch(actions.changeChordShadow(shadowChord))
    store.dispatch(actions.changeBassShadow(self.__getBass()))

    store.dispatch(actions.changeSettingLoading(False))
    self.state['loadingSetting'] = False

  def playChord(self, button):
    self.state['activeChord'] = button
    self.__setChordType()
    self.stopChord(buttonUp=False)
    notes = self.__getChord(button)
    self.__sendNotesOn(notes, player='chord')
    self.__updateBass()
    store.dispatch(actions.playChord(notes))

    self.state['playingChordNotes'] = notes
    self.state['chordIsPlaying'] = True

  def __setNumVoices(self, chordNotes):
    return chordNotes[:self.voices] if self.voices < len(chordNotes) else chordNotes

  def __setOctave(self, chordNotes):
    return [note + (self.octave * 12) for note in chordNotes]

  def playBass(self):
    self.stopBass(buttonUp=False)
    bassNote = self.__getBass()

    self.__sendNotesOn([bassNote], player='bass')
    store.dispatch(actions.playBass(bassNote))

    self.state['playingBassNote'] = bassNote
    self.state['bassIsPlaying'] = True

  def stopChord(self, buttonUp=True):
    if not buttonUp or not self.state['hold']:
      if self.state['chordIsPlaying']:
        self.__sendNotesOff(self.state['playingChordNotes'], player='chord')
        store.dispatch(actions.stopChord())
        self.state['playingChordNotes'] = []
        self.state['chordIsPlaying'] = False
  
  def stopBass(self, buttonUp=True):
    if not buttonUp or not self.state['hold']:
      if self.state['bassIsPlaying']:
        self.__sendNotesOff([self.state['playingBassNote']], player='bass')
        store.dispatch(actions.stopBass())
        self.state['playingBassNote'] = None
        self.state['bassIsPlaying'] = False 

  def setModulation(self, side):
    if self.state['modulation'] != side:
      scale = self.state['scale']
      if side != "none": scale = self.modulations[side].applyToScale()
      store.dispatch(actions.changeModulation({
        'scale': scale,
        'side': side
      }))
      self.state['modulation'] = side
      self.__setChordType()
      self.__updateChord()
      self.__updateBass()

  def setSecondary(self, side):
    if self.state['secondary'] != side:
      self.state['secondary'] = side
      self.__setChordType()
      self.__updateChord()
      self.__updateBass()

  def setAlternate(self, alternate):
    if self.state['alternate'] != alternate:
      self.state['alternate'] = alternate
      self.__setChordType()
      self.__updateChord()
      self.__updateBass()

  def incrementInversion(self):
    newInversion = self.state['inversion'] + 1
    if abs(newInversion) <= self.state['inversionRange']:
      self.setInversion(newInversion)

  def decrementInversion(self):
    newInversion = self.state['inversion'] - 1
    if abs(newInversion) <= self.state['inversionRange']:
      self.setInversion(newInversion)

  def setInversion(self, inversion):
    if (not self.state['inversionLock']):
      if inversion != self.state['inversion']:
        range = self.state['inversionRange']
        self.state['inversion'] = max(min(inversion, range), -1*range)
        self.__updateChord()
        store.dispatch(actions.changeInversion(self.state['inversion']))

  def setAnalogInversion(self, value):
    inversion = self.processInversionValue(value, type='chord')
    self.setInversion(inversion)

  def setAnalogBassPosition(self, value):
    position = self.processInversionValue(value, type='bass')
    self.setBassPosition(position)
  
  def setInversionRange(self, range):
    range = max(min(range, MAX_INVERSION_RANGE), 0)
    self.state['inversionRange'] = range
    self.state['inversion'] = max(min(self.state['inversion'], range), -1*range) 
    self.__updateChord()
    store.dispatch(actions.changeInversion(self.state['inversion']))
    store.dispatch(actions.changeInversionRange(self.state['inversionRange']))

  def incrementBassPosition(self):
    newPosition = self.state['bassPosition'] + 1
    if abs(newPosition) <= self.state['bassRange']:
      self.setBassPosition(newPosition)

  def decrementBassPosition(self):
    newPosition = self.state['bassPosition'] - 1
    if abs(newPosition) <= self.state['bassRange']:
      self.setBassPosition(newPosition)
    
  def setBassPosition(self, position):
    if position != self.state['bassPosition']:
      range = self.state['bassRange']
      self.state['bassPosition'] = max(min(position, range), -1*range)
      self.__updateBass()
      store.dispatch(actions.changeBassPosition(self.state['bassposition']))

  def setBassRange(self, range):
    range = max(min(range, MAX_BASS_RANGE), 0)
    self.state['bassRange'] = range
    self.state['bassPosition'] = max(min(self.state['bassPosition'], range), -1*range)   
    self.__updateBass()
    store.dispatch(actions.changeInversion(self.state['bassPosition']))
    store.dispatch(actions.changeInversionRange(self.state['bassRange']))

  def setSpread(self, spread):
    maxSpread = SPREAD_STEPS_PER_OCTAVE * MAX_SPREAD_OCTAVES - 1
    spread = max(min(spread, maxSpread), 0)
    self.state['spread'] = spread
    self.__updateChord()
    store.dispatch(actions.changeSpread(self.state['spread']))
  
  def incrementSpread(self):
    self.setSpread(self.state['spread'] + 1)

  def decrementSpread(self):
    self.setSpread(self.state['spread'] - 1)

  def setKey(self, key):
    key = key % 12
    if self.state['key'] != key:
      self.state['key'] = key
      store.dispatch(actions.changeKey(key))
      self.__setChordType()
      self.__updateChord()
      self.__updateBass()

  def incrementKey(self):
    self.setKey(self.state['key'] + 1)

  def decrementKey(self):
    self.setKey(self.state['key'] + 11)

  def setVoiceCount(self, count):
    count = max(min(count, MAX_VOICE_COUNT), 1)
    self.state['voiceCount'] = count
    self.__updateChord()
    store.dispatch(actions.changeVoiceCount(self.state['voiceCount']))
  
  def incrementVoiceCount(self):
    self.setVoiceCount(self.state['voiceCount'] + 1)
  
  def decrementVoiceCount(self):
    self.setVoiceCount(self.state['voiceCount'] - 1)
  
  def setChordChannel(self, channel):
    channel = max(min(channel, 16), 0)
    self.state['chordChannel'] = channel
    self.__updateChord()
    store.dispatch(actions.changeChordChannel(channel))

  def setBassChannel(self, channel):
    channel = max(min(channel, 16), 0)
    self.state['bassChannel'] = channel
    self.__updateBass()
    store.dispatch(actions.changeBassChannel(channel))

  def setChordOctave(self, octave):
    self.state['chordOctave'] = max(min(octave, MAX_OCTAVE_SHIFT), -1*MAX_OCTAVE_SHIFT)
    self.__updateChord()
    store.dispatch(actions.changeChordOctave(self.state['chordOctave']))

  def incrementChordOctave(self):
    self.setChordOctave(self.state['chordOctave'] + 1)
  
  def decrementChordOctave(self):
    self.setChordOctave(self.state['chordOctave'] + 1)
  
  def toggleHold(self):
    if self.state['hold']:
      self.state['hold'] = False
      self.stopChord(buttonUp=False)
      self.stopBass(buttonUp=False)
    else:
      self.state['hold'] = True
    store.dispatch(actions.changeHold(self.state['chordOctave']))
  
  def toggleInversionLock(self):
    self.state['inversionLock'] = not self.state['inversionLock']
    store.dispatch(actions.changeInversionLock(self.state['inversionLock']))

  def processInversionValue(self, rawValue, type='chord'):
    maxSteps = self.state['inversionRange'] if type == 'chord' else self.state['bassRange']
    lastValue = self.state['inversion'] if type == 'chord' else self.state['bassPosition']

    # converts to an integer in the correct inversion range
    def getValue(x):
      return math.floor(((x+1)/2)*((2*maxSteps)+1)) - maxSteps

    # snap processed value back into current window if     
    value = getValue(rawValue)
    snap = (1.0 / (maxSteps + 1)) * INVERSION_SNAP
    if value == lastValue + 1:
      rawValue -= snap
      value = getValue(rawValue)
    if value == lastValue - 1:
      rawValue += snap
      value = getValue(rawValue)

    return value

  def subscribe(self, callback):
    self.callbacks.append(callback)

  def __findScaleNotesForKey(self, key):
    scaleNotes = []
    for note in self.state['scale']:
      scaleNotes.append((note + key) % 12)
    return scaleNotes

  def __findScaleNotes(self):
    scaleNotes = {}
    allScaleNotes = {}
    for key in range(0, 12):
      scaleNotes[key] = self.__findScaleNotesForKey(key)
      allScaleNotes[key] = Chord.findAllNotes(scaleNotes[key])
    return scaleNotes, allScaleNotes
  
  
  def __sendNotesOn(self, notes, player):
    message = {
      'type': 'on',
      'notes': notes,
      'player': player
    }
    self.__sendMessage(message)

  def __sendNotesOff(self, notes, player):
    message = {
      'type': 'off',
      'notes': notes,
      'player': player
    }
    self.__sendMessage(message)
    
  def __sendMessage(self, message):
    for callback in self.callbacks:
      callback(message)
  
  def __mod12(self, notes):
    newNotes = []
    for note in notes:
      newNotes.append(note % 12)
    return newNotes

  def __getChordType(self, button):
    chord = self.chords[button]
    # secondary inactive
    if (self.state['secondary'] == "none"):
      if (self.state['modulation'] == "none"):
        return chord.getNoteTypes(self.state), chord.getRoot(self.state['key'])
      else:
        modulation = self.modulations[self.state['modulation']]
        rootNote = modulation.applyOne(chord.getRoot(self.state['key']), self.__getScale()) % 12
        chordNotes = self.__mod12(modulation.apply(chord.getNoteTypes(self.state), self.__getScale()))
        return chordNotes, rootNote
    # secondary is active
    else:
      modKey = "default"
      if (self.state['modulation'] == "left"):
        modKey = "leftModulation"
      elif (self.state['modulation'] == "left"):
        modKey = "rightModulation"
      secondary = self.secondaries[self.state['secondary']][button][modKey]
      chordRoot = chord.getRoot(self.state['key'])
      rootType = secondary.getRoot(chordRoot)
      chordType = secondary.getNoteTypes(self.state, chordRoot)
      chordType.sort()
      return chordType, rootType

  def __setChordType(self):
    chord, root = self.__getChordType(self.state['activeChord'])
    if chord != self.chordType or root != self.rootType:
      self.chordType, self.rootType = chord, root
      store.dispatch(actions.changeChordType({'chord': chord, 'root': root}))

  def __getChord(self, button):
    chord = self.chords[button]
    # secondary inactive
    if (self.state['secondary'] == "none"):
      if (self.state['modulation'] == "none"):
        chord = chord.getChord(self.state)
      else:
        modulation = self.modulations[self.state['modulation']]
        chord = modulation.apply(chord.getChord(self.state), self.__getScale())
    # secondary is active
    else:
      modKey = "default"
      if (self.state['modulation'] == "left"):
        modKey = "leftModulation"
      elif (self.state['modulation'] == "left"):
        modKey = "rightModulation"
      secondary = self.secondaries[self.state['secondary']][button][modKey]
      chord = secondary.getChord(self.state, chord.getRoot(self.state['key']))
    
    chordAdjustedNumVoices = self.__setNumVoices(chord)
    chordAdjustedOctaves = self.__setOctave(chordAdjustedNumVoices)
    return chordAdjustedOctaves

  def __setNumVoices(self, chordNotes):
    return chordNotes[:self.state['voiceCount']] if self.state['voiceCount'] < len(chordNotes) else chordNotes

  def __setOctave(self, chordNotes):
    return [note + (self.state['chordOctave'] * 12) for note in chordNotes]
 
  def __getScale(self):
    return self.state['scaleNotes'][self.state['key']]
  
  def __getBass(self):
    chord = self.chords[self.state['activeChord']]
    if (self.state['secondary'] == "none"):
      if (self.state['modulation'] == "none"):
        return chord.getBass(self)
      else:
        modulation = self.modulations[self.state['modulation']]
        return modulation.applyOne(chord.getBass(self), self.__getScale())
    # secondary is active
    else:
      modKey = "default"
      if (self.state['modulation'] == "left"):
        modKey = "leftModulation"
      elif (self.state['modulation'] == "left"):
        modKey = "rightModulation"

      secondary = self.secondaries[self.state['secondary']][self.state['activeChord']][modKey]
      return secondary.getBass(self.state, chord.getRoot(self.state['key']))

  def __updateChord(self):
    if (self.state['chordIsPlaying']):
      self.playChord(self.state['activeChord'])
    else:
      notes = self.__getChord(self.state['activeChord'])
      store.dispatch(actions.changeChordShadow(notes))

  def __updateBass(self):
    if (self.state['bassIsPlaying']):
      self.playBass()
    else:
      note = self.__getBass()
      store.dispatch(actions.changeBassShadow(note))