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
      'velocityDeviation': 5, # 'standard deviation for random velocity'

      'strumMode': 'random', # 'random', 'regular', 'off'
      'strumInterval': 0.5, # time beween notes or spread of distribution
      'strumOrder' : 'up', # 'up', 'down', or 'random'
      'playingNotes': [],
      'scheduledNotes': [],

      'distributeChannels': False,
      'occupiedChannels': {},
      'noteChannels': {},
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

  def handleNotesMessage(self, message):
    notes, player, type = message['notes'], message['player'], message['type']
    if type == 'on':
      channelMap, channel = None, None     
      if self.state['distributeChannels']:
        self.__distributeChannels(notes)
      else:
        channel = self.state['chordChannel'] if player is 'chord' else self.state['bassChannel']

      intervals = None
      if self.state['strumMode'] != 'off' and player == 'chord':
        print('strum is good')
        intervals = self.__getIntervals(len(notes))
        print(intervals)
        notes.sort()

      for i, note in enumerate(notes):
        velocity = self.__getVelocity()
        noteChannel = channel
        if channelMap is not None:
          noteChannel = channelMap[note]
        self.state['noteChannels'][note] = noteChannel
        channelCommand = self.__combineCommandAndChannel(NOTE_ON, noteChannel)
        if intervals is None:
          print('no strum')
          self.state['playingNotes'].append(note)
          self.midiOut.send_message([channelCommand, note, velocity])
        else:
          print('strum')
          j = i if self.state['strumDirection'] != 'down' else (len(notes) - 1) -i
          asyncio.ensure_future(self.__scheduleNote(
            command = channelCommand,
            note = note,
            velocity = velocity,
            interval = intervals[j]
          ))
    elif type == 'off':
      self.state['scheduledNotes'] = []
      if self.state['distributeChannels']:
        self.__openChannels(notes)

      for note in notes:
        velocity = 0
        noteChannel = self.state['noteChannels'][note]
        channelCommand = self.__combineCommandAndChannel(NOTE_OFF, noteChannel)
        self.midiOut.send_message([channelCommand, note, velocity])
        self.state['noteChannels'][note] = None
        self.state['playingNotes'].remove(note)


  def setAfterTouch(self, value):
    self.state['afterTouch'] = math.floor(((value+1) / 2)*128)

  def getCCSetter(self, cc):
    def setCCValue(value):
      self.state['CCValues'][cc] = math.floor(((value+1) / 2)*128)
    return setCCValue

  def __sendAftertouch(self):
    if self.state['afterTouch'] != self.state['lastSentAfterTouch']:
      for note in self.state['playingNotes']:
        channel = self.state['noteChannels'][note]
        channelCommand = self.__combineCommandAndChannel(POLY_AFTERTOUCH, channel)
        self.midiOut.send_message([channelCommand, note, self.state['afterTouch']])
      self.state['lastSentAfterTouch'] = self.state['afterTouch']
        
  def __sendCCValues(self):
    for cc, val in self.state['CCValues'].items():
      if val != self.state['lastSentCCValues'][cc]:
        for note in self.state['playingNotes']:
          channel = self.state['noteChannels'][note]
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

  def __distributeChannels(self, notes):
    channelMap = {}
    for note in notes:
      for channel in range(0, 16):
        if self.state['occupiedChannels'][channel] is None:
          self.state['occupiedChannels'][channel] = note
          channelMap[note] = channel
          break
    return channelMap
  
  def __openChannels(self, notes):
    for note in notes:
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
      intervals = intervals.sort() if self.state['strumOrder'] != 'random' else intervals
      print(intervals)
    elif self.state['strumMode'] == 'regular':
      intervals = self.__getRegularIntervals(n)
      intervals = random.permutation(intervals) if self.state['strumOrder'] == 'random' else intervals
    return intervals

  def __getVelocity(self):
    if self.state['velocityMode'] == 'constant':
      return self.state['velocity']
    elif self.state['velocityMode'] == 'random':
      return self.__getRandomVelocity()

  async def __scheduleNote(self, command, note, velocity, interval):
    self.state['scheduledNotes'].append(note)
    await asyncio.sleep(interval)
    if note in self.state['scheduledNotes']:
      self.midiOut.send_message([command, note, velocity])
      self.state['playingNotes'].append(note)
      self.state['scheduledNotes'].remove(note)