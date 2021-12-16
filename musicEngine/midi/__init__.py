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
      'velocityMode': 'constant', # 'constant' or 'random'
      'velocityDeviation': 5, # 'standard deviation for random velocity'

      'strumMode': 'random', # 'random', 'regular', 'off'
      'strumInterval': 0.05, # time beween notes or spread of distribution
      'strumOrder' : 'up', # 'up', 'down', or 'random'
      'playingNotes': [],
      'scheduledNotes': [],

      'distributeChannels': False,
      'occupiedChannels': {},
      'chordNoteChannels': {},
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
    store.dispatch()
    if len(self.availablePorts) >= 2:
      self.midiOut.open_port(1)

  def handleNotesMessage(self, message):
    notes, player, type = message['note'], message['player'], message['type']
    channelMap = None
    if type == 'off':
      channelMap = self.__openChannels(notes) if self.state['distributeChannels'] else None
    else:
      channelMap = self.__distributeChannels(notes) if self.state['distributeChannels'] else None
    channel = self.state['chordChannel'] if player is 'chord' else self.state['bassChannel']
    command = NOTE_ON if type == 'on' else NOTE_OFF

    if command == NOTE_OFF:
      self.state['scheduledNotes'] = []

    strum = self.state['strumMode'] != 'off' and command == NOTE_ON and player == 'chord'
    intervals = self.__getIntervals(len(notes)) if strum else None
    notes = notes.sort() if strum else notes

    for i, note in message['notes'].enumerate():
      velocity = self.__getVelocity()
      noteChannel = channel
      if channelMap is not None:
        noteChannel = channelMap[note]
      commandWithChannel = (command & 0xf0) | (noteChannel & 0xf)
      if intervals is None:
        self.midiOut.send_message([commandWithChannel, note, velocity])
      else:
        j = i if self.state['strumDirection'] != 'down' else (len(notes) - 1) -i
        asyncio.ensure_future(self.__scheduleNote(
          command = commandWithChannel,
          note = note,
          velocity = velocity,
          interval = intervals[j]
        ))

  def setAfterTouch(self, value):
    self.state['afterTouch'] = math.floor(((value+1) / 2)*128)

  def getCCSetter(self, cc):
    def setCCValue(value):
      self.state['CCValues'][cc] = math.floor(((value+1) / 2)*128)
    return setCCValue

  async def loop(self):
    while True:
      for note in self.state['playingNotes']:
        if self.state['afterTouch'] != self.state['lastSentAfterTouch']:
          self.state['lastSentAfterTouch'] = self.state['afterTouch']
          

  def __distributeChannels(self, notes):
    channelMap = {}
    for note in notes:
      for channel in range(0, 16):
        if self.state['occupiedChannels'][channel] is not None:
          self.state['occupiedChannels'][channel] = note
          channelMap[note] = channel
          break
    return channelMap
  
  def __openChannels(self, notes):
    channelMap = {}
    for channel, note in self.state['occupiedChannels'].items():
      if note in notes:
        channelMap[note] = channel
        self.state['occupiedChannels'][channel] = None
    return channelMap

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
      intervals = self.__getRandomIntervals(len(n))
      intervals = intervals.sort() if self.state['strumOrder'] != 'random' else intervals
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
    asyncio.sleep(interval)
    if note in self.state['scheduledNotes']:
      self.midiOut.send_message([command, note, velocity])
      self.state['playingNotes'].append(note)
      self.state['scheduledNotes'].remove(note)




