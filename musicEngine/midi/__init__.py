from rtmidi import MidiOut
from rtmidi.midiconstants import *

class Midi():
  def __init__(self):
    self.midiOut = MidiOut()
    self.availablePorts = self.midiOut.get_ports()