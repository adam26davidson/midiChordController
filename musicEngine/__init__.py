from .chordEngine import ChordEngine
from .midi import Midi
from redux import store

class MusicEngine():

  def __init__(self):
    self.chordEngine = ChordEngine()
    self.midi = Midi()

    self.chordEngine.subscribe(self.midi.handleNotesMessage)

  def start(self):
    self.midi.start()

  def commandMap(self, key):
    map = {
      "SOUTH_CHORD_ON": lambda: self.chordEngine.playChord('south'),
      "SOUTH_CHORD_OFF": self.chordEngine.stopChord,
      "WEST_CHORD_ON": lambda: self.chordEngine.playChord('west'),
      "WEST_CHORD_OFF": self.chordEngine.stopChord,
      "NORTH_CHORD_ON": lambda: self.chordEngine.playChord('west'),
      "NORTH_CHORD_OFF": self.chordEngine.stopChord,
      "EAST_CHORD_ON": lambda: self.chordEngine.playChord('west'),
      "EAST_CHORD_OFF": self.chordEngine.stopChord,

      "LEFT_SECONDARY_ON": lambda: self.chordEngine.setSecondary('left'),
      "RIGHT_SECONDARY_ON": lambda: self.chordEngine.setSecondary('right'),
      "SECONDARY_OFF": lambda: self.chordEngine.setSecondary('none'),

      "OCTAVE_UP": self.chordEngine.incrementChordOctave,
      "OCTAVE_DOWN": self.chordEngine.decrementChordOctave,

      "INCREMENT_BASS_POSITION": self.chordEngine.incrementBassPosition,
      "DECREMENT_BASS_POSITION": self.chordEngine.decrementBassPosition,

      "INCREMENT_VOICE_COUNT": self.chordEngine.incrementVoiceCount,
      "DECREMENT_VOICE_COUNT": self.chordEngine.decrementVoiceCount,

      "INCREMENT_SETTING": self.chordEngine.incrementSetting,
      "DECREMENT_SETTING": self.chordEngine.decrementSetting,

      "INCREMENT_KEY": self.chordEngine.incrementKey,
      "DECREMENT_KEY": self.chordEngine.decrementKey,
      
      "INCREMENT_SPREAD": self.chordEngine.incrementSpread,
      "DECREMENT_SPREAD": self.chordEngine.decrementSpread,

      "RIGHT_MODULATION_ON": lambda: self.chordEngine.setModulation('right'),
      "RIGHT_MODULATION_OFF": lambda: self.chordEngine.setModulation('none'),
      "LEFT_MODULATION_ON": lambda: self.chordEngine.setModulation('left'),
      "LEFT_MODULATION_OFF": lambda: self.chordEngine.setModulation('none'),

      "ALTERNATE_ON": lambda: self.chordEngine.setAlternate(True),
      "ALTERNATE_OFF": lambda: self.chordEngine.setAlternate(False),
      "BASS_ON": self.chordEngine.playBass,
      "BASS_OFF": self.chordEngine.stopBass,

      "TOGGLE_INVERSION_LOCK": self.chordEngine.toggleInversionLock,
      "TOGGLE_HOLD": self.chordEngine.toggleHold,

      "UPDATE_INVERSION": self.chordEngine.toggleInversionLock,
      "UPDATE_AFTERTOUCH": self.midi.setAfterTouch,

      "UPDATE_MIDI_CC_1": self.midi.getCCSetter(1),
      "UPDATE_MIDI_CC_2": self.midi.getCCSetter(2)
    }
    return map[key]

  def controllerEventHandler(self, event):
    controllers = store.get_state()['controllerManager']['controllers']
    meMap = None
    for controller in controllers:
      if controller['role'] == 'primary':
        meMap = controller['meMap']['map']
    
    command = meMap[event['name']]
    if 'value' in event.keys():
      self.commandMap(command)(event['value'])
    else:
      self.commandMap(command)()
