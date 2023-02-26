from rtmidi import MidiOut, MidiIn
from redux import store
from redux.actions import musicEngine as actions
from pyrsistent import thaw
from rtmidi.midiconstants import *
from constants import *
from numpy import random
from datetime import datetime
import copy
import asyncio, math

class Midi():
  def __init__(self):
    self.utilityMidiOut = MidiOut()
    self.midiOutInstances = []
    self.state = {
      'midiOutputConnected': False,
      'midiOutputControllerNames': [],

      'velocity': 100, # constant velocity or center of random distribution
      'velocityMode': 'random', # 'constant' or 'random'
      'velocityDeviation': 15, # 'standard deviation for random velocity'

      'playingChordNotes': [],
      'playingBassNote': None,

      'distributeChannels': False,
      'occupiedChannels': {},
      'distChordChannels': {},
      'chordChannel': 0,
      'bassChannel': 0,

      'aftertouchMode': 'channel', # 'channel' or 'poly'. default is to use channel aftertouch
      'afterTouch': 0,
      'lastSentAfterTouch': 0,
      'CCValues': {},
      'lastSentCCValues': {}
    }

    for channel in range(0, 16):
      if self.state['bassChannel'] == channel:
        self.state['occupiedChannels'][channel] = True
      else:
        self.state['occupiedChannels'][channel] = False
    
    for note in range(0, 128):
      self.state['distChordChannels'][note] = 0

    store.subscribe(self.__handleStoreUpdate)

  def start(self):
    self.availableOutputPorts = self.utilityMidiOut.get_ports()
    print(self.availableOutputPorts)

    for i in range(1, len(self.availableOutputPorts)):
      midiOut = MidiOut()
      midiOut.open_port(i)
      self.midiOutInstances.append(midiOut)
      self.state['midiOutputControllerNames'].append(self.availableOutputPorts[i])

    asyncio.ensure_future(self.__loop())

  def handleMessage(self, message):
    # if not self.state['midiOutputConnected']:
    #   return None

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
    if (meState['velocity'] != self.state['velocity']):
      self.__setVelocity(meState['velocity'])
    if (meState['velocityMode'] != self.state['velocityMode']):
      self.__setVelocityMode(meState['velocityMode'])
    if (meState['velocityDeviation'] != self.state['velocityDeviation']):
      self.__setVelocityDeviation(meState['velocityDeviation'])
    if (meState['aftertouchMode'] != self.state['aftertouchMode']):
      self.__setAftertouchMode(meState['aftertouchMode'])
    

  async def __loop(self):
    while True:
      ports = self.utilityMidiOut.get_ports()
      if self.availableOutputPorts == ports:
        self.__sendAfterTouch()
        self.__sendCCValues()
      else:
        self.availableOutputPorts = ports
        self.__reconnect()
      await asyncio.sleep(MIDI_STEP)

  def __reconnect(self):
    print("RECONNECTING TO MIDI OUTPUTS")
    for midiOut in self.midiOutInstances:
      if midiOut.is_port_open():
        midiOut.close_port()
      midiOut.delete()
    
    self.availableOutputPorts = self.utilityMidiOut.get_ports()
    print(self.availableOutputPorts)

    self.midiOutInstances = []
    self.state['midiOutputControllerNames'] = []
    for i in range(1, len(self.availableOutputPorts)):
      midiOut = MidiOut()
      midiOut.open_port(i)
      self.midiOutInstances.append(midiOut)
      self.state['midiOutputControllerNames'].append(self.availableOutputPorts[i])

  def __setBassChannel(self, channel):
    if (channel < 0 or channel > 15):
      store.dispatch(actions.changeBassChannel(self.state['bassChannel']))
    else:
      
      # if chord is playing and distribute channels is on, stop chord
      if self.state['distributeChannels'] and len(self.state['playingChordNotes']) > 0:
        chordNotes = copy.deepcopy(self.state['playingChordNotes'])
        for note in chordNotes:
          self.__noteOff(note, 'chord')

      # open up old bass channel
      self.state['occupiedChannels'][self.state['bassChannel']] = False
      # close new bass channel
      self.state['occupiedChannels'][channel] = True

      #update bass to play on new channel, set state bass channel
      if self.state['playingBassNote']:
        note = self.state['playingBassNote']
        self.__noteOff(note, 'bass')
        self.state['bassChannel'] = channel
        self.__noteOn(note, 'bass')
      else:
        self.state['bassChannel'] = channel
      
      # replay distributed chord
      if self.state['distributeChannels'] and len(self.state['playingChordNotes']) > 0:
        for note in chordNotes:
          self.__noteOn(note, 'chord')
  
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
      for note in chordNotes:
        self.__noteOff(note, 'chord')
      self.state['distributeChannels'] = distribute
      for note in chordNotes:
        self.__noteOn(note, 'chord')
    else:
      self.state['distributeChannels'] = distribute

  def __setVelocity(self, velocity):
    self.state['velocity'] = velocity
  
  def __setVelocityMode(self, mode):
    self.state['velocityMode'] = mode

  def __setVelocityDeviation(self, deviation):
    self.state['velocityDeviation'] = deviation
  
  def __setAftertouchMode(self, aftertouchMode):
    self.state['aftertouchMode'] = aftertouchMode
  
  def __sendMidiMessage(self, message):
    # self.midiOut.send_message(message)
    for midiOut in self.midiOutInstances:
      midiOut.send_message(message)

  def __noteOff(self, note, player):
    noteChannel = self.__getNoteChannel(note, player, 'off')
    #print(f'OFF -- note: {note}, channel: {noteChannel}, player: {player}')
    channelCommand = self.__combineCommandAndChannel(NOTE_OFF, noteChannel)
    self.__sendMidiMessage([channelCommand, note, 0])
    self.__storeNoteOff(note, player)
  
  def __noteOn(self, note, player):
    velocity = self.__getVelocity()
    noteChannel = self.__getNoteChannel(note, player, 'on')
    #print(f'ON -- note: {note}, channel: {noteChannel}, player: {player}')
    channelCommand = self.__combineCommandAndChannel(NOTE_ON, noteChannel)
    self.__sendMidiMessage([channelCommand, note, velocity])
    self.__storeNoteOn(note, player, noteChannel)
    self.__sendAfterTouch(force=True)
    if player == 'chord':
      store.dispatch(actions.playChord(self.state['playingChordNotes']))

  def __storeNoteOn(self, note, player, channel=None):
    if player == 'chord' and note not in self.state['playingChordNotes']:
      self.state['playingChordNotes'].append(note)
    else:
      self.state['playingBassNote'] = note
    if self.state['distributeChannels'] and player == 'chord':
      self.state['distChordChannels'][note] = channel

  def __storeNoteOff(self, note, player):
    if self.state['distributeChannels'] and player == 'chord':
      self.__openChannel(note, player)
    if player == 'chord':
      if note in self.state['playingChordNotes']:
        self.state['playingChordNotes'].remove(note)
    else:
      self.state['playingBassNote'] = None

    # this is here just in case a channel gets stuck on occupied
    if self.state['distributeChannels'] \
      and len(self.state['playingChordNotes']) == 0 \
      and self.state['playingBassNote'] == None:
      for channel in range(0, 16):
        if channel != self.state['bassChannel']:
          self.state['occupiedChannels'][channel] = False
  
  def __getNoteChannel(self, note, player, type):
    if player == 'chord':
      if self.state['distributeChannels']:
        if type == 'on':
          return self.__distributeChannel()
        else:
          return self.state['distChordChannels'][note]
      else:
        return self.state['chordChannel']
    elif player == 'bass':
      return self.state['bassChannel']

  def __sendChannelAfterTouch(self, force=False):
    if not force and (self.state['afterTouch'] == self.state['lastSentAfterTouch']):
      return None

    aftertouchValue = self.state['afterTouch']
    if self.state['distributeChannels']:
      channels = filter(
        lambda x: self.state['occupiedChannels'][x], 
        self.state['occupiedChannels'].keys())
      for channel in channels:
        channelCommand = self.__combineCommandAndChannel(CHANNEL_PRESSURE, channel)
        self.__sendMidiMessage([channelCommand, aftertouchValue])
    else:
      channel = self.state['chordChannel']
      channelCommand = self.__combineCommandAndChannel(CHANNEL_PRESSURE, channel)
      self.__sendMidiMessage([channelCommand, aftertouchValue])

    if self.state['playingBassNote']:
      channel = self.state['bassChannel']
      channelCommand = self.__combineCommandAndChannel(CHANNEL_PRESSURE, channel)
      self.__sendMidiMessage([channelCommand, aftertouchValue])

    self.state['lastSentAfterTouch'] = self.state['afterTouch']

  def __sendPolyphonicAftertouch(self, force=False):
    if not force and (self.state['afterTouch'] == self.state['lastSentAfterTouch']):
      return None

    # send poly aftertouch for each chord note
    for note in self.state['playingChordNotes']:
      channel = self.state['chordChannel']
      if self.state['distributeChannels']:
        channel = self.state['distChordChannels'][note]
      channelCommand = self.__combineCommandAndChannel(POLY_AFTERTOUCH, channel)
      self.__sendMidiMessage([channelCommand, note, self.state['afterTouch']])

    #send poly aftertouch for bass note
    if self.state['playingBassNote']:
      bassNote = self.state['playingBassNote']
      channel = self.state['bassChannel']
      channelCommand = self.__combineCommandAndChannel(POLY_AFTERTOUCH, channel)
      self.__sendMidiMessage([channelCommand, bassNote, self.state['afterTouch']])

    self.state['lastSentAfterTouch'] = self.state['afterTouch']
  
  def __sendAfterTouch(self, force=False):
    if self.state['aftertouchMode']=='poly':
      self.__sendPolyphonicAftertouch(force)
    else:
      self.__sendChannelAfterTouch(force)

  def __sendCCValues(self):
    for cc, val in self.state['CCValues'].items():
      if val != self.state['lastSentCCValues'][cc]:
        for channel in range(0, 16):
          channelCommand = self.__combineCommandAndChannel(CONTROL_CHANGE, channel)
          self.__sendMidiMessage([channelCommand, cc, val])  
        self.state['lastSentCCValues'][cc] = val
  
  def __combineCommandAndChannel(self, command, channel):
    return ((command & 0xf0) | (channel & 0xf))

  def __distributeChannel(self):
      for channel in range(0, 16):
        #print(f"{channel}: {self.state['occupiedChannels'][channel]}")
        if not self.state['occupiedChannels'][channel]:
          self.state['occupiedChannels'][channel] = True
          return channel
  
  def __openChannel(self, note, player):
    if player == 'chord':
      channel = self.state['distChordChannels'][note]
      self.state['occupiedChannels'][channel] = False

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