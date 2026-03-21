import asyncio
import traceback

from numpy import random
from pyrsistent import thaw

from musicEngine.chordEngine.chordEngineMessage import ChordEngineMessage, ChordMessageType, ChordPlayer
from redux import store


class RhythmEngine:
  def __init__(self):
    self.callbacks = []
    self.scheduledNotes = ScheduledNotes()
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
        self.__handleChordOffSync(message.notes)
      elif message.type == ChordMessageType.ON:
        self.__handleChordOn(message.notes)
    elif message.player == ChordPlayer.BASS:
      if message.type == ChordMessageType.OFF:
        self.__handleBassOff(message.notes)
      elif message.type == ChordMessageType.ON:
        self.__handleBassOn(message.notes)

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
    self.scheduledNotes.cancelAll()
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
      if self.state['strumOrder'] != 'random':
        intervals.sort()
    elif self.state['strumMode'] == 'regular':
      intervals = self.__getRegularIntervals(n)
      intervals = random.permutation(intervals) if self.state['strumOrder'] == 'random' else intervals
    elif self.state['strumMode'] == 'off':
      intervals = [0] * n
    return intervals

  async def __scheduleMessage(self, message, delay, generation):
    await asyncio.sleep(delay)

    # Only send if no cancelAll has happened since this was scheduled
    if self.scheduledNotes.generation == generation:
      self.__sendMessage(message)

  def __handleChordOn(self, notes):
      self.scheduledNotes.cancelAll()
      gen = self.scheduledNotes.generation
      if (self.state['strumMode'] != 'off'):
        intervals = None
        intervals = self.__getIntervals(len(notes))
        notes.sort()
        for i, note in enumerate(notes):
          j = i if self.state['strumOrder'] != 'down' else (len(notes) - 1) -i
          message = {'note': note, 'type': 'on', 'player': 'chord'}
          task = asyncio.create_task(self.__scheduleMessage(message, intervals[j], gen))
          task.add_done_callback(self.__handleTaskException)
      else:
        for note in notes:
          message = {'note': note, 'type': 'on', 'player': 'chord'}
          self.__sendMessage(message)

  def __handleTaskException(self, task):
    if not task.cancelled() and task.exception() is not None:
      print("Exception in scheduled note task:")
      traceback.print_exception(type(task.exception()), task.exception(), task.exception().__traceback__)

  def __handleChordOffSync(self, notes):
    self.scheduledNotes.cancelAll()
    for note in notes:
      message = {'note': note, 'type': 'off', 'player': 'chord'}
      self.__sendMessage(message)


  def __handleBassOn(self, notes):
    self.__sendMessage({'note': notes[0], 'type': 'on', 'player': 'bass'})

  def __handleBassOff(self, notes):
    self.__sendMessage({'note': notes[0], 'type': 'off', 'player': 'bass'})

class ScheduledNotes:
  """Simple generation-based cancellation. Incrementing the generation
  invalidates all previously scheduled notes without needing locks."""

  def __init__(self):
    self.generation = 0

  def cancelAll(self):
    self.generation += 1
