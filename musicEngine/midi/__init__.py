from rtmidi import MidiOut, MidiIn
from redux import store
from rtmidi.midiconstants import *
from constants import *
from numpy import random, copy
import asyncio, math

class Midi():
  def __init__(self):
    self.midiOut = MidiOut()
    self.state = {
      'velocity': 100, # constant velocity or center of random distribution
      'velocityMode': 'random', # 'constant' or 'random'
      'velocityDeviation': 15, # 'standard deviation for random velocity'

      'playingChordNotes': [],
      'playingBassNote': None,
      'scheduledNotes': [],

      'distributeChannels': False,
      'occupiedChannels': {},
      'distChordChannels': {},
      'distBassChannel': 0,
      'chordChannel': 0,
      'bassChannel': 0,

      'afterTouch': 0,
      'lastSentAfterTouch': 0,
      'CCValues': {},
      'lastSentCCValues': {}
    }

    for channel in range(0, 15):
      self.state['occupiedChannels'][channel] = None

  def start(self):
    self.availableOutputPorts = self.midiOut.get_ports()
    print(self.availableOutputPorts)
    if len(self.availableOutputPorts) > 0:
      self.midiOut.open_port(0)
    asyncio.ensure_future(self.__loop())

  def handleMessage(self, message):
    note, player, type = message['note'], message['player'], message['type']
    if type == 'on':
      self.__noteOn(note, player)
    elif type == 'off':
      self.__noteOff(note, player)
  
  def setAfterTouch(self, value):
    self.state['afterTouch'] = math.floor(((value+1) / 2)*128)

  def getCCSetter(self, cc):
    def setCCValue(value):
      self.state['CCValues'][cc] = math.floor(((value+1) / 2)*128)
    return setCCValue

  def __noteOff(self, note, player):
    noteChannel = self.__getNoteChannel(note, player, type)
    channelCommand = self.__combineCommandAndChannel(NOTE_OFF, noteChannel)
    self.midiOut.send_message([channelCommand, note, 0])
    self.__storeNoteOff(note, player, noteChannel)
  
  def __noteOn(self, note, player):
    velocity = self.__getVelocity()
    noteChannel = self.__getNoteChannel(note, player, 'on')
    channelCommand = self.__combineCommandAndChannel(NOTE_ON, noteChannel)
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
      if player == 'chord':
        self.state['distChordChannels'][note] = None
      else:
        self.state['distBassChannel'] = None
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
        self.__openChannel(note)
        if player == 'chord':
          return self.state['distChordChannels'][note]
        else:
          return self.state['distBassChannel']
    elif player == 'chord':
      return self.state['chordChannel']
    elif player == 'bass':
      return self.state['bassChannel']

  def __sendAftertouch(self):
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
        
  def __sendCCValues(self):
    for cc, val in self.state['CCValues'].items():
      if val != self.state['lastSentCCValues'][cc]:
        for note in self.state['playingChordNotes']:
          channel = self.state['chordChannel']
          if self.state['distributeChannels']:
            channel = self.state['distChordChannels'][note]
          channelCommand = self.__combineCommandAndChannel(CONTROL_CHANGE, channel)
          self.midiOut.send_message([channelCommand, cc, val])
        if self.state['playingBassNote'] is not None:
          channel = self.state['bassChannel']
          if self.state['distributeChannels']:
            channel = self.state['distBassChannel']
          channelCommand = self.__combineCommandAndChannel(CONTROL_CHANGE, channel)
          self.midiOut.send_message([channelCommand, cc, val])
        self.state['lastSentCCValues'][cc] = val

  async def __loop(self):
    while True:
      self.__sendAftertouch()
      self.__sendCCValues()
      await asyncio.sleep(MIDI_STEP)
  
  def __combineCommandAndChannel(self, command, channel):
    return ((command & 0xf0) | (channel & 0xf))

  def __distributeChannel(self, note):
      for channel in range(0, 16):
        if self.state['occupiedChannels'][channel] is None:
          self.state['occupiedChannels'][channel] = note
          return channel
  
  def __openChannel(self, note):
    channel = self.state['noteChannels'][note]
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