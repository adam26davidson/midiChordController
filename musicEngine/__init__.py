from .chordEngine import ChordEngine
import pydux
from store import store

class MusicEngine():

  def __init__(self):
    self.chordEngine = ChordEngine()

  def controllerEventHandler(self):
    store.get_state()['controllers']