from constants import *
from redux import store
from .chordDisplay import ChordDisplay
from .keyboard import Keyboard
from .inversion import Inversion
from .spread import Spread
from .textDisplay import TextDisplay
from pyrsistent import thaw
import asyncio
import tkinter as tk

class Display():
  def __init__(self):
    self.height = 480
    self.width = 800
    self.root = tk.Tk()

    self.root.overrideredirect(True)
    self.root.overrideredirect(False)

    if FULLSCREEN:
      self.root.attributes("-fullscreen", True)
      self.root.wm_attributes("-topmost", 1)
      self.root.focus_set()
    else:
      self.root.geometry("800x480")

    def close_escape(event=None):
      print("escaped")
      self.root.destroy()

    self.root.bind("<Escape>", close_escape)


    self.root.configure(bg='black')

    self.state = {
      'chordType': {'notes': [], 'root': 0},
      'shadowChordNotes' : [],
      'playingChordNotes' : [],
      'shadowBassNote' : 48,
      'playingBassNote' : None,

      'inversionThumbValue' : 0,
      'bassThumbValue' : 0,

      'bassPosition': 0,
      'bassRange': 4,
      'inversion': 0,
      'inversionRange': 4,

      'key': 0,
      'scale': []
    }

    self.keyboard = Keyboard(master=self.root)
    self.spread = Spread(master=self.root)
    self.inversion = Inversion(master=self.root)
    self.bassPosition = Inversion(master=self.root)
    self.chordDisplay = ChordDisplay(master=self.root)
    self.textDisplay = TextDisplay(master=self.root)

    store.subscribe(self.__handleStoreUpdate)

  def start(self):
    asyncio.ensure_future(self.__mainLoop())

  async def __mainLoop(self):
    while True:
      print('main display loop')
      self.__setInversionThumb()
      self.__setBassPositionThumb()
      self.chordDisplay.runAnimationStep()
      self.root.update()
      await asyncio.sleep(ANIMATION_STEP)

  def __handleStoreUpdate(self):
    meState = thaw(store.get_state()['musicEngine'])

    if meState['chordShadow'] != self.state['shadowChordNotes']:
      self.__setChordShadow(meState['chordShadow'])
    elif meState['chordNotes'] != self.state['playingChordNotes']:
      if len(meState['chordNotes']) > 0:
        self.__playChord(meState['chordNotes'])
      else:
        self.__stopChord()
    elif meState['bassShadow'] != self.state['shadowBassNote']:
      self.__setBassShadow(meState['bassShadow'])
    elif meState['bassNote'] != self.state['playingBassNote']:
      if meState['bassNote'] != None:
        self.__playBass(meState['bassNote'])
      else:
        self.__stopBass()
    elif meState['chordType']['notes'] != self.state['chordType']['notes'] or \
      meState['chordType']['root'] != self.state['chordType']['root']:
      self.__setChord(meState['chordType']['notes'], meState['chordType']['root'])
    elif meState['inversion'] != self.state['inversion']:
      self.__setInversion(meState['inversion'])
    elif meState['bassPosition'] != self.state['bassPosition']:
      self.__setBassPosition(meState['bassPosition'])
    elif meState['inversionRange'] != self.state['inversionRange']:
      self.__setInversionRange(meState['inversionRange'], meState['inversion'])
    elif meState['bassRange'] != self.state['bassRange']:
      self.__setBassPositionRange(meState['bassRange'], meState['bassPosition'])
    elif meState['key'] != self.state['key']:
      self.__setKey(meState['key'])
    elif meState['scale'] != self.state['scale']:
      print('display scale set')
      self.__setScale(meState['scale'])

  def setController(self, text):
    self.textDisplay.setController(text)

  def setSetting(self, text):
    self.textDisplay.setSetting(text)

  def setAlt(self, alt):
    self.textDisplay.setAlt(alt)

  def setShift(self, shift):
    self.textDisplay.setShift(shift)
  
  def __setKey(self, key):
    self.state['key'] = key
    self.chordDisplay.setKey(key)

  def __setScale(self, scale):
    self.state['scale'] = scale
    self.chordDisplay.setScale(scale)

  def __setInversionRange(self, range, inversion):
    self.state['inversionRange'] = range
    self.state['inversion'] = inversion
    self.inversion.setMax(range, inversion)
  
  def __setInversion(self, inversion):
    self.state['inversion'] = inversion
    self.inversion.setActiveRegion(inversion)

  def __storeInversionThumb(self, value):
    self.state['inversionThumbValue'] = value

  def __setInversionThumb(self):
    self.inversion.positionThumb(self.state['inversionThumbValue'])

  def __setBassPositionRange(self, range, position):
    self.state['bassRange'] = range
    self.state['bassPosition'] = position
    self.bassPosition.setMax(range, position)
  
  def __setBassPosition(self, position):
    self.state['bassPosition'] = position
    self.bassPosition.setActiveRegion(position)

  def __storeBassPositionThumb(self, value):
    self.state['bassThumbValue'] = value

  def __setBassPositionThumb(self):
    self.bassPosition.positionThumb(self.state['bassThumbValue'])

  def __stopChordShadow(self):
    resetNotes = []
    for note in self.state['shadowChordNotes']:
      if note != self.state['shadowBassNote']:
        resetNotes.append(note)
    self.keyboard.reset(resetNotes)
    self.state['shadowChordNotes'] = []

  def __stopBassShadow(self):
    noteInPlayingChord = self.state['playingChordNotes'].count(self.state['shadowBassNote']) != 0
    noteInShadowChord = self.state['shadowChordNotes'].count(self.state['shadowBassNote']) != 0
    if (not noteInPlayingChord) and (not noteInShadowChord) and self.state['shadowBassNote'] != None:
      self.keyboard.reset([self.state['shadowBassNote']])
    self.state['shadowBassNote'] = None

  def __setChord(self, chord, root):
    self.state['chordType'] = {'notes': chord, 'root': root}
    self.keyboard.setChord(chord, root)
    self.chordDisplay.setChord(chord, root)
  
  def __playChord(self, notes):
    self.__stopChordShadow()
    self.keyboard.play(notes)
    self.state['playingChordNotes'] = notes
    self.chordDisplay.playChord()
  
  def __playBass(self, note):
    self.__stopBassShadow()
    self.keyboard.play([note])
    self.chordDisplay.playBass(note)
    self.state['playingBassNote'] = note

  def __stopChord(self, notes):
    self.state['shadowChordNotes'] = notes
    self.keyboard.setShadow(notes)
    self.state['playingChordNotes'] = []
    self.chordDisplay.setChordShadow()

  def __stopBass(self, note):
    if self.state['playingChordNotes'].count(note) == 0:
      self.keyboard.setShadow([note])
    self.chordDisplay.setBassShadow(note)
    self.state['shadowBassNote'] = note
    self.state['playingBassNote'] = None

  def __setChordShadow(self, notes):
    self.keyboard.reset(self.state['shadowChordNotes'])
    self.state['shadowChordNotes'] = notes
    self.keyboard.setShadow(notes)
    self.chordDisplay.setChordShadow()

  def __setBassShadow(self, note):
    self.__stopBassShadow()
    self.state['shadowBassNote'] = note
    noteInPlayingChord = self.state['playingChordNotes'].count(note) != 0
    if not noteInPlayingChord:
      self.keyboard.setShadow([note])
    self.chordDisplay.setBassShadow(note)

  def setModulation(self, newScale, side):
    self.chordDisplay.setModulation(newScale, side)

