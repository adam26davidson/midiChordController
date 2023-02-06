from rtmidi import MidiOut, MidiIn
from redux import store
from redux.actions import musicEngine as actions
from pyrsistent import thaw
from rtmidi.midiconstants import *
from constants import *
from numpy import random
import copy
import asyncio, math

class Midi():
  def __init__(self):
    self.midiOut = MidiOut()
    self.state = {
      'midiOutputConnected': False,
      'midiOutputControllerName': '',
      'midiOutputPortNumber': 1, # default

      'velocity': 100, # constant velocity or center of random distribution
      'velocityMode': 'random', # 'constant' or 'random'
      'velocityDeviation': 15, # 'standard deviation for random velocity'

      'playingChordNotes': [],
      'playingBassNote': None,

      'distributeChannels': False,
      'occupiedChannels': {},
      'distChordChannels': {},
      'distBassChannel': 0,
      'chordChannel': 0,
      'bassChannel': 0,

      'usePolyphonicAfterTouch': False, # default is to use channel aftertouch
      'afterTouch': 0,
      'lastSentAfterTouch': 0,
      'CCValues': {},
      'lastSentCCValues': {}
    }

    for channel in range(0, 16):
      self.state['occupiedChannels'][channel] = None
    
    for note in range(0, 128):
      self.state['distChordChannels'][note] = 0

    store.subscribe(self.__handleStoreUpdate)

  def start(self):
    self.availableOutputPorts = self.midiOut.get_ports()
    print(self.availableOutputPorts)
    if len(self.availableOutputPorts) > 1:
      self.midiOut.open_port(self.state['midiOutputPortNumber'])
      self.state['midiOutputControllerName'] = self.availableOutputPorts[self.state['midiOutputPortNumber']]
      self.state['midiOutputConnected'] = True
    asyncio.ensure_future(self.__loop())

  def handleMessage(self, message):
    if not self.state['midiOutputConnected']:
      return None

    note, player, type = message['note'], message['player'], message['type']
    if type == 'on':
      self.__noteOn(note, player)
    elif type == 'off':
      self.__noteOff(note, player)
  
  def setAfterTouch(self, value):
    self.state['afterTouch'] = math.floor(((value+1) / 2)*128)

  def getCCSetter(self, cc):
    self.state['lastSentCCValues'][cc] = None
    def setCCValue(value):
      self.state['CCValues'][cc] = math.floor(((value+1) / 2)*128)
    return setCCValue
  
  def __handleStoreUpdate(self):
    state = store.get_state()
    meState = thaw(state['musicEngine'])
    if (meState['bassChannel'] != self.state['bassChannel']):
      self.__setBassChannel(meState['bassChannel'])
    if (meState['chordChannel'] != self.state['chordChannel']):
      self.__setChordChannel(meState['chordChannel'])
    if (meState['distributeChannels'] != self.state['distributeChannels']):
      self.__setDistributeChannels(meState['distributeChannels'])

  async def __loop(self):
    while True:
      self.availableOutputPorts = self.midiOut.get_ports()
      if self.state['midiOutputControllerName'] in self.availableOutputPorts:
        self.__sendAfterTouch()
        self.__sendCCValues()
      else:
        self.__reconnect()
      await asyncio.sleep(MIDI_STEP)

  def __reconnect(self):
    if self.midiOut.is_port_open():
      self.midiOut.close_port()
      self.state['midiOutputConnected'] = False

    if len(self.availableOutputPorts) > 1:
      self.midiOut.open_port(self.state['midiOutputPortNumber'])
      self.state['midiOutputControllerName'] = self.availableOutputPorts[self.state['midiOutputPortNumber']]
      self.state['midiOutputConnected'] = True
    else:
      self.state['midiOutputControllerName'] = ''

  def __setBassChannel(self, channel):
    if (channel < 0 or channel > 15):
      store.dispatch(actions.changeBassChannel(self.state['bassChannel']))
    else:
      if self.state['playingBassNote']:
        note = self.state['playingBassNote']
        self.__noteOff(note, 'bass')
        self.state['bassChannel'] = channel
        self.__noteOn(note, 'bass')
      else:
        self.state['bassChannel'] = channel
  
  def __setChordChannel(self, channel):
    if (channel < 0 or channel > 15):
      store.dispatch(actions.changeChordChannel(self.state['chordChannel']))
    else:
      if len(self.state['playingChordNotes']) > 0:
        notes = copy.deepcopy(self.state['playingChordNotes'])
        for note in notes:
          self.__noteOff(note, 'chord')
        self.state['chordChannel'] = channel
        for note in notes:
          self.__noteOn(note, 'chord')
      else:
        self.state['chordChannel'] = channel

  def __setDistributeChannels(self, distribute):
    if len(self.state['playingChordNotes']) > 0 or self.state['playingBassNote']:
      chordNotes = copy.deepcopy(self.state['playingChordNotes'])
      bassNote = self.state['playingBassNote']
      self.__noteOff(bassNote, 'chord')
      for note in chordNotes:
        self.__noteOff(note, 'chord')
      self.state['distributeChannels'] = distribute
      for note in chordNotes:
        self.__noteOn(note, 'chord')
      self.__noteOn(bassNote, 'chord')
    else:
      self.state['distributeChannels'] = distribute

  def __noteOff(self, note, player):
    noteChannel = self.__getNoteChannel(note, player, 'off')
    print(f'OFF -- note: {note}, channel: {noteChannel}, player: {player}')
    channelCommand = self.__combineCommandAndChannel(NOTE_OFF, noteChannel)
    self.midiOut.send_message([channelCommand, note, 0])
    self.__storeNoteOff(note, player, noteChannel)
  
  def __noteOn(self, note, player):
    velocity = self.__getVelocity()
    noteChannel = self.__getNoteChannel(note, player, 'on')
    print(f'ON -- note: {note}, channel: {noteChannel}, player: {player}')
    channelCommand = self.__combineCommandAndChannel(NOTE_ON, noteChannel)
    #print(str(note) + '- ON')
    self.midiOut.send_message([channelCommand, note, velocity])
    self.__storeNoteOn(note, player, noteChannel)

  def __storeNoteOn(self, note, player, channel=None):
    if player == 'chord':
      self.state['playingChordNotes'].append(note)
    else:
      self.state['playingBassNote'] = note
    if self.state['distributeChannels']:
      if player == 'chord':
        self.state['distChordChannels'][note] = channel
      else:
        self.state['distBassChannel'] = channel

  def __storeNoteOff(self, note, player, channel=None):
    if self.state['distributeChannels']:
      self.__openChannel(note, player)
      # if player == 'chord':
      #   self.state['distChordChannels'][note] = None
      # else:
      #   self.state['distBassChannel'] = None
    if player == 'chord':
      if note in self.state['playingChordNotes']:
        self.state['playingChordNotes'].remove(note)
    else:
      self.state['playingBassNote'] = None
  
  def __getNoteChannel(self, note, player, type):
    if self.state['distributeChannels']:
      if type == 'on':
        return self.__distributeChannel(note)
      else:
        if player == 'chord':
          return self.state['distChordChannels'][note]
        else:
          return self.state['distBassChannel']
    elif player == 'chord':
      return self.state['chordChannel']
    elif player == 'bass':
      return self.state['bassChannel']

  def __sendChannelAfterTouch(self):
    if self.state['afterTouch'] == self.state['lastSentAfterTouch']:
      return None

    aftertouchValue = self.state['afterTouch']
    if self.state['distributeChannels']:
      channels = self.state['occupiedChannels']
      for channel in channels:
        channelCommand = self.__combineCommandAndChannel(CHANNEL_PRESSURE, channel)
        self.midiOut.send_message([channelCommand, aftertouchValue])
    else:
      channel = self.state['chordChannel']
      channelCommand = self.__combineCommandAndChannel(CHANNEL_PRESSURE, channel)
      self.midiOut.send_message([channelCommand, aftertouchValue])

    if self.state['playingBassNote']:
      channel = self.state['distBassChannel'] if self.state['distributeChannels'] else self.state['bassChannel']
      channelCommand = self.__combineCommandAndChannel(CHANNEL_PRESSURE, channel)
      self.midiOut.send_message([channelCommand, aftertouchValue])

    self.state['lastSentAfterTouch'] = self.state['afterTouch']

  def __sendPolyphonicAftertouch(self):
    if self.state['afterTouch'] != self.state['lastSentAfterTouch']:
      for note in self.state['playingChordNotes']:
        channel = self.state['chordChannel']
        if self.state['distributeChannels']:
          channel = self.state['distChordChannels'][note]
        channelCommand = self.__combineCommandAndChannel(POLY_AFTERTOUCH, channel)
        self.midiOut.send_message([channelCommand, note, self.state['afterTouch']])
      if self.state['playingBassNote'] is not None:
        bassNote = self.state['playingBassNote']
        channel = self.state['bassChannel']
        if self.state['distributeChannels']:
          channel = self.state['distBassChannel']
        channelCommand = self.__combineCommandAndChannel(POLY_AFTERTOUCH, channel)
        self.midiOut.send_message([channelCommand, bassNote, self.state['afterTouch']])
      self.state['lastSentAfterTouch'] = self.state['afterTouch']
  
  def __sendAfterTouch(self):
    if self.state['usePolyphonicAfterTouch']:
      self.__sendPolyphonicAftertouch()
    else:
      self.__sendChannelAfterTouch()

  def __sendCCValues(self):
    for cc, val in self.state['CCValues'].items():
      if val != self.state['lastSentCCValues'][cc]:
        for channel in range(0, 16):
          channelCommand = self.__combineCommandAndChannel(CONTROL_CHANGE, channel)
          self.midiOut.send_message([channelCommand, cc, val])  
        self.state['lastSentCCValues'][cc] = val
  
  def __combineCommandAndChannel(self, command, channel):
    return ((command & 0xf0) | (channel & 0xf))

  def __distributeChannel(self, note):
      for channel in range(0, 16):
        if self.state['occupiedChannels'][channel] is None:
          self.state['occupiedChannels'][channel] = note
          return channel
  
  def __openChannel(self, note, player):
    if player == 'chord':
      channel = self.state['distChordChannels'][note]
      self.state['occupiedChannels'][channel] = None
    elif player == 'bass':
      channel = self.state['distBassChannel']
      self.state['occupiedChannels'][channel] = None

  def __getRandomVelocity(self):
    value = random.normal(
      loc = self.state['velocity'],
      scale = self.state['velocityDeviation']
    )
    return max(min(value, 127), 0)

  def __getVelocity(self):
    if self.state['velocityMode'] == 'constant':
      return self.state['velocity']
    elif self.state['velocityMode'] == 'random':
      return self.__getRandomVelocity()