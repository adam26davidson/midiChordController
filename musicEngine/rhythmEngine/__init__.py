from numpy import random
import asyncio
import time

class RhythmEngine():
  def __init__(self):
    self.callbacks = []
    self.scheduledNotesLock = asyncio.Lock()
    self.state = {
      'strumMode': 'random', # 'random', 'regular', 'off'
      'strumInterval': 0.05, # time beween notes or spread of distribution
      'strumOrder' : 'random', # 'up', 'down', or 'random'
      'scheduledNotes': []
    }

  def subscribe(self, callback):
    self.callbacks.append(callback)

  # takes a dict 'message' with the following keys:
  #   'notes' (array of midi note values), 
  #   'type' (on or off), and 
  #   'player' (chord or bass)
  def handleMessage(self, message):
    if message['player'] == 'chord':
      if message['type'] == 'off':
        self.__handleChordOff(message['notes'])
      elif message['type'] == 'on':
        self.__handleChordOn(message['notes'])
    elif message['player'] == 'bass':
      if message['type'] == 'off':
        self.__handleBassOff(message['notes'])
      elif message['type'] == 'on':
        self.__handleBassOn(message['notes'])

  # takes a dict with the following keys:
  #   'note' (midi note value), 
  #   'type' (on or off), and 
  #   'player' (chord or bass)
  def __sendMessage(self, message):
    for callback in self.callbacks:
      callback(message)

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
  
  async def __scheduleMessage(self, message, delay):
    async with self.scheduledNotesLock:
      self.state['scheduledNotes'].append(message['note'])
    await asyncio.sleep(delay)
    async with self.scheduledNotesLock:
      if message['note'] in self.state['scheduledNotes']:
        self.__sendMessage(message)
        self.state['scheduledNotes'].remove(message['note'])

  def __handleChordOn(self, notes):
      # async with self.scheduledNotesLock:
      #   self.state['scheduledNotes'] = []
      intervals = None
      if self.state['strumMode'] != 'off':
        intervals = self.__getIntervals(len(notes))
        notes.sort()
      for i, note in enumerate(notes):  
        if intervals is None:
          self.__sendMessage({'note': note, 'type': 'on', 'player': 'chord'})
        else:
          j = i if self.state['strumOrder'] != 'down' else (len(notes) - 1) -i
          message = {'note': note, 'type': 'on', 'player': 'chord'}
          asyncio.ensure_future(self.__scheduleMessage(message, intervals[j]))

  async def scheduledNotesOff(self, notes):
    for note in notes:
      # remove scheduled note
      async with self.scheduledNotesLock:
        if note in self.state['scheduledNotes']:
          self.state['scheduledNotes'].remove(note)
  
  def __handleChordOff(self, notes):
    asyncio.ensure_future(self.scheduledNotesOff(notes))
    for note in notes:
      #send note off
      message = {'note': note,'type': 'off','player': 'chord'}
      self.__sendMessage(message)

  
  def __handleBassOn(self, notes):
    self.__sendMessage({'note': notes[0], 'type': 'on', 'player': 'bass'})
  
  def __handleBassOff(self, notes):
    self.__sendMessage({'note': notes[0], 'type': 'off', 'player': 'bass'})