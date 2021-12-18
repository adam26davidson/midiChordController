from rtmidi import MidiOut, MidiIn
from redux import store
from rtmidi.midiconstants import *
from constants import *
from numpy import random
import asyncio, math

class Midi():
  def __init__(self):
    self.midiOut = MidiOut()
    self.state = {
      'velocity': 100, # constant velocity or center of random distribution
      'velocityMode': 'random', # 'constant' or 'random'
      'velocityDeviation': 15, # 'standard deviation for random velocity'

      'strumMode': 'random', # 'random', 'regular', 'off'
      'strumInterval': 0.5, # time beween notes or spread of distribution
      'strumOrder' : 'down', # 'up', 'down', or 'random'
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
    if len(self.availableOutputPorts) >= 2:
      self.midiOut.open_port(1)
    asyncio.ensure_future(self.__loop())

  def storeNoteOn(self, note, player, channel=None):
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

  def handleNotesMessage(self, message):
    notes, player, type = message['notes'], message['player'], message['type']
    if type == 'on': 
      intervals = None
      if self.state['strumMode'] != 'off' and player == 'chord':
        intervals = self.__getIntervals(len(notes))
        notes.sort()
        
      for i, note in enumerate(notes):  
        velocity = self.__getVelocity()
        noteChannel = self.__getNoteChannel(note, player, type)
        channelCommand = self.__combineCommandAndChannel(NOTE_ON, noteChannel)
        if intervals is None:
          self.midiOut.send_message([channelCommand, note, velocity])
          self.storeNoteOn(note, player, noteChannel)
        else:
          j = i if self.state['strumOrder'] != 'down' else (len(notes) - 1) -i
          asyncio.ensure_future(self.__scheduleNote(
            command = channelCommand,
            note = note,
            velocity = velocity,
            interval = intervals[j],
            channel = noteChannel
          ))

    elif type == 'off':
      if player == 'chord':
        self.state['scheduledNotes'] = []
      for note in notes:
        noteChannel = self.__getNoteChannel(note, player, type)
        channelCommand = self.__combineCommandAndChannel(NOTE_OFF, noteChannel)
        self.midiOut.send_message([channelCommand, note, 0])
        self.__storeNoteOff(note, player, noteChannel)


  def setAfterTouch(self, value):
    self.state['afterTouch'] = math.floor(((value+1) / 2)*128)

  def getCCSetter(self, cc):
    def setCCValue(value):
      self.state['CCValues'][cc] = math.floor(((value+1) / 2)*128)
    return setCCValue

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

  def __getRandomIntervals(self, n):
    values = random.normal(
      loc = 0,
      scale = self.state['strumInterval'],
      size = n
    )
    return [abs(v) for v in values]
  
  def __getRegularIntervals(self, n):
    return [i*self.state['strumInterval'] for i in range(n)]

  def __getIntervals(self, n):
    intervals = []
    if self.state['strumMode'] == 'random':
      intervals = self.__getRandomIntervals(n)
      if self.state['strumOrder'] != 'random': intervals.sort()
    elif self.state['strumMode'] == 'regular':
      intervals = self.__getRegularIntervals(n)
      intervals = random.permutation(intervals) if self.state['strumOrder'] == 'random' else intervals
    return intervals

  def __getVelocity(self):
    if self.state['velocityMode'] == 'constant':
      return self.state['velocity']
    elif self.state['velocityMode'] == 'random':
      return self.__getRandomVelocity()

  async def __scheduleNote(self, command, note, velocity, interval, channel=None):
    self.state['scheduledNotes'].append(note)
    await asyncio.sleep(interval)
    if note in self.state['scheduledNotes']:
      self.midiOut.send_message([command, note, velocity])
      self.storeNoteOn(note, 'chord', channel)
      self.state['scheduledNotes'].remove(note)