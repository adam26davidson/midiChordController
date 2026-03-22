from __future__ import annotations

import asyncio
import logging
from typing import Callable, TypedDict

from numpy import random

from music_engine.chord_engine.chord_engine_message import ChordEngineMessage, ChordMessageType, ChordPlayer
from redux import get_music_engine_state, store

logger = logging.getLogger(__name__)


class RhythmMessage(TypedDict):
    note: int
    type: str
    player: str


class RhythmState(TypedDict):
    strumMode: str
    strumInterval: float
    strumOrder: str


class RhythmEngine:
  def __init__(self) -> None:
    self.callbacks: list[Callable[[RhythmMessage], None]] = []
    self.scheduled_notes = ScheduledNotes()
    self.state: RhythmState = {
      'strumMode': 'regular', # 'random', 'regular', 'off'
      'strumInterval': 0.02, # time beween notes or spread of distribution
      'strumOrder' : 'random', # 'up', 'down', or 'random'
    }
    store.subscribe(self.__handle_store_update)

  def subscribe(self, callback: Callable[[RhythmMessage], None]) -> None:
    self.callbacks.append(callback)

  # takes a dict 'message' with the following keys:
  #   'notes' (array of midi note values),
  #   'type' (on or off), and
  #   'player' (chord or bass)
  def handle_message(self, message: ChordEngineMessage) -> None:
    if message.player == ChordPlayer.CHORD:
      if message.type == ChordMessageType.OFF:
        self.__handle_chord_off_sync(message.notes)
      elif message.type == ChordMessageType.ON:
        self.__handle_chord_on(message.notes)
    elif message.player == ChordPlayer.BASS:
      if message.type == ChordMessageType.OFF:
        self.__handle_bass_off(message.notes)
      elif message.type == ChordMessageType.ON:
        self.__handle_bass_on(message.notes)

  # takes a dict with the following keys:
  #   'note' (midi note value),
  #   'type' (on or off), and
  #   'player' (chord or bass)
  def __send_message(self, message: RhythmMessage) -> None:
    for callback in self.callbacks:
      callback(message)

  def __handle_store_update(self) -> None:
    me_state = get_music_engine_state()
    if (me_state['strumMode'] != self.state['strumMode']):
      self.__set_strum_mode(me_state['strumMode'])
    if (me_state['strumInterval'] != self.state['strumInterval']):
      self.__set_strum_interval(me_state['strumInterval'])
    if (me_state['strumOrder'] != self.state['strumOrder']):
      self.__set_strum_order(me_state['strumOrder'])

  def __set_strum_mode(self, mode: str) -> None:
    self.scheduled_notes.cancel_all()
    self.state['strumMode'] = mode

  def __set_strum_interval(self, interval: float) -> None:
    self.state['strumInterval'] = interval

  def __set_strum_order(self, order: str) -> None:
    self.state['strumOrder'] = order

  def __get_random_intervals(self, n: int) -> list[float]:
    values = random.normal(
      loc = 0,
      scale = self.state['strumInterval'],
      size = n
    )
    return [abs(v) for v in values]

  def __get_regular_intervals(self, n: int) -> list[float]:
    interval = self.state['strumInterval']
    return [i * interval for i in range(n)]

  def __get_intervals(self, n: int) -> list[float]:
    intervals: list[float] = []
    if self.state['strumMode'] == 'random':
      intervals = self.__get_random_intervals(n)
      if self.state['strumOrder'] != 'random':
        intervals.sort()
    elif self.state['strumMode'] == 'regular':
      intervals = self.__get_regular_intervals(n)
      intervals = random.permutation(intervals) if self.state['strumOrder'] == 'random' else intervals
    elif self.state['strumMode'] == 'off':
      intervals = [0.0] * n
    return intervals

  async def __schedule_message(self, message: RhythmMessage, delay: float, generation: int) -> None:
    await asyncio.sleep(delay)

    # Only send if no cancel_all has happened since this was scheduled
    if self.scheduled_notes.generation == generation:
      self.__send_message(message)

  def __handle_chord_on(self, notes: list[int]) -> None:
      self.scheduled_notes.cancel_all()
      gen = self.scheduled_notes.generation
      if (self.state['strumMode'] != 'off'):
        intervals = None
        intervals = self.__get_intervals(len(notes))
        notes.sort()
        for i, note in enumerate(notes):
          j = i if self.state['strumOrder'] != 'down' else (len(notes) - 1) -i
          msg: RhythmMessage = {'note': note, 'type': 'on', 'player': 'chord'}
          task = asyncio.create_task(self.__schedule_message(msg, intervals[j], gen))
          task.add_done_callback(self.__handle_task_exception)
      else:
        for note in notes:
          msg2: RhythmMessage = {'note': note, 'type': 'on', 'player': 'chord'}
          self.__send_message(msg2)

  def __handle_task_exception(self, task: asyncio.Task[None]) -> None:
    if not task.cancelled():
      exc = task.exception()
      if exc is not None:
        logger.error("Exception in scheduled note task:", exc_info=exc)

  def __handle_chord_off_sync(self, notes: list[int]) -> None:
    self.scheduled_notes.cancel_all()
    for note in notes:
      msg: RhythmMessage = {'note': note, 'type': 'off', 'player': 'chord'}
      self.__send_message(msg)


  def __handle_bass_on(self, notes: list[int]) -> None:
    self.__send_message({'note': notes[0], 'type': 'on', 'player': 'bass'})

  def __handle_bass_off(self, notes: list[int]) -> None:
    self.__send_message({'note': notes[0], 'type': 'off', 'player': 'bass'})

class ScheduledNotes:
  """Simple generation-based cancellation. Incrementing the generation
  invalidates all previously scheduled notes without needing locks."""

  def __init__(self) -> None:
    self.generation: int = 0

  def cancel_all(self) -> None:
    self.generation += 1
