from musicEngine.chordEngine.chordEngineMessage import ChordEngineMessage, ChordMessageType, ChordPlayer
from numpy import random
import asyncio
import time
import uuid
from pyrsistent import thaw
from redux import store

class RhythmEngine():
  def __init__(self):
    self.callbacks = []
    self.scheduledNotes = ScheduledNotes()
    self.chordLock = asyncio.Lock()
    self.state = {
      'strumMode': 'regular', # 'random', 'regular', 'off'
      'strumInterval': 0.02, # time beween notes or spread of distribution
      'strumOrder' : 'random', # 'up', 'down', or 'random'
    }
    store.subscribe(self.__handleStoreUpdate)

  def subscribe(self, callback):
    self.callbacks.append(callback)

  # takes a dict 'message' with the following keys:
  #   'notes' (array of midi note values), 
  #   'type' (on or off), and 
  #   'player' (chord or bass)
  def handleMessage(self, message: ChordEngineMessage):
    if message.player == ChordPlayer.CHORD:
      if message.type == ChordMessageType.OFF:
        if self.state['strumMode'] == 'off':
          self.__handleChordOffSync(message['notes'])
        else:
          asyncio.ensure_future(self.__handleChordOff(message['notes']))
      elif message.type == ChordMessageType.ON:
        self.__handleChordOn(message['notes'])
    elif message.player == ChordPlayer.BASS:
      if message.type == ChordMessageType.OFF:
        self.__handleBassOff(message['notes'])
      elif message.type == ChordMessageType.ON:
        self.__handleBassOn(message['notes'])

  # takes a dict with the following keys:
  #   'note' (midi note value), 
  #   'type' (on or off), and 
  #   'player' (chord or bass)
  def __sendMessage(self, message):
    for callback in self.callbacks:
      callback(message)
    
  def __handleStoreUpdate(self):
    state = store.get_state()
    meState = thaw(state['musicEngine'])
    if (meState['strumMode'] != self.state['strumMode']):
      self.__setStrumMode(meState['strumMode'])
    if (meState['strumInterval'] != self.state['strumInterval']):
      self.__setStrumInterval(meState['strumInterval'])
    if (meState['strumOrder'] != self.state['strumOrder']):
      self.__setStrumOrder(meState['strumOrder'])

  def __setStrumMode(self, mode):
    self.scheduledNotes.removeAll()
    self.state['strumMode'] = mode
  
  def __setStrumInterval(self, interval):
    self.state['strumInterval'] = interval
  
  def __setStrumOrder(self, order):
    self.state['strumOrder'] = order

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
    elif self.state['strumMode'] == 'off':
      intervals = [0] * n
    return intervals
  
  async def __scheduleMessage(self, message, delay):
    scheduledNote = ScheduledNote(message['note'])
    await self.scheduledNotes.addScheduledNote(scheduledNote)

    await asyncio.sleep(delay)

    if await self.scheduledNotes.isNoteStillScheduled(scheduledNote):
      self.__sendMessage(message)
      await self.scheduledNotes.removeScheduledNote(scheduledNote)

  def __handleChordOn(self, notes):
      self.scheduledNotes.removeAll()
      if (self.state['strumMode'] != 'off'):
        intervals = None
        intervals = self.__getIntervals(len(notes))
        notes.sort()
        for i, note in enumerate(notes):  
          j = i if self.state['strumOrder'] != 'down' else (len(notes) - 1) -i
          message = {'note': note, 'type': 'on', 'player': 'chord'}
          asyncio.ensure_future(self.__scheduleMessage(message, intervals[j]))
      else:
        for note in notes:
          message = {'note': note, 'type': 'on', 'player': 'chord'}
          self.__sendMessage(message)
  
  def __handleChordOffSync(self, notes):
    self.scheduledNotes.removeAll()
    for note in notes:
      message = {'note': note, 'type': 'off', 'player': 'chord'}
      self.__sendMessage(message)
  
  async def __handleChordOff(self, notes):
    self.__handleChordOffSync(notes)

  
  def __handleBassOn(self, notes):
    self.__sendMessage({'note': notes[0], 'type': 'on', 'player': 'bass'})
  
  def __handleBassOff(self, notes):
    self.__sendMessage({'note': notes[0], 'type': 'off', 'player': 'bass'})
  
class ScheduledNotes():
  notes = {}

  def __init__(self):
    self.lock = asyncio.Lock()
    for note in range(0, 128):
      self.notes[str(note)] = []

  async def addScheduledNote(self, scheduledNote):
    async with self.lock:
      self.notes[str(scheduledNote.note)].append(scheduledNote)

  async def removeScheduledNote(self, scheduledNote):
    async with self.lock:
      scheduledNotes = self.notes[str(scheduledNote.note)]
      for note in scheduledNotes:
        if note.id == scheduledNote.id:
          scheduledNotes.remove(scheduledNote)
          return None

  async def removeNote(self, note):
    async with self.lock:
      self.notes[str(note)] = []

  async def removeNotes(self, notes):
    async with self.lock:
      for note in notes:
        self.notes[str(note)] = []
  
  async def isNoteStillScheduled(self, scheduledNote):
    async with self.lock:
      for note in self.notes[str(scheduledNote.note)]:
        if note.id == scheduledNote.id:
          return True
      return False
  
  def removeAll(self):
    for note in range(0, 128):
      self.notes[str(note)] = []


class ScheduledNote():
  def __init__(self, note):
    self.note = note
    self.id = f"{note}-{time.time_ns()}-{random.randint(1000000)}"
