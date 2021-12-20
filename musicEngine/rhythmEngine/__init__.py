from numpy import random
import asyncio

class RhythmEngine():
  def __init__(self):
    self.callbacks = []
    self.state = {
      'strumMode': 'random', # 'random', 'regular', 'off'
      'strumInterval': 0.1, # time beween notes or spread of distribution
      'strumOrder' : 'down', # 'up', 'down', or 'random'
      'scheduledNotes': [],
    }

  def subscribe(self, callback):
    self.callbacks.append(callback)

  def sendMessage(self, message):
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
  
  def __scheduleNote(self, note, interval):
    asyncio.sleep(interval)
    self.sendMessage({'note': note, 'type': 'on', 'player': 'chord'})

  def handleChordOn(self, notes):
      self.state['scheduledNotes'] = []
      intervals = None
      if self.state['strumMode'] != 'off':
        intervals = self.__getIntervals(len(notes))
        notes.sort()
      for i, note in enumerate(notes):  
        if intervals is None:
          self.sendMessage({'note': note, 'type': 'on', 'player': 'chord'})
        else:
          j = i if self.state['strumOrder'] != 'down' else (len(notes) - 1) -i
          self.sendMessage({'note': note, 'type': 'on', 'player': 'chord', 'delay': intervals[j]})
          asyncio.ensure_future(self.__scheduleNote(note, intervals[j]))