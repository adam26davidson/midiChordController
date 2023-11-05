from enum import Enum
from typing import List

from constants import SPREAD_STEPS_PER_OCTAVE
from musicEngine.chordEngine.externalChordEngine.modules.noteHistory.noteHistoryState import NoteHistoryState
from musicEngine.chordEngine.internalChordEngine.modules.modulations.modulationsState import ModulationsState
from musicEngine.chordEngine.internalChordEngine.modules.secondaries.secondariesState import SecondariesState
from musicEngine.chordEngine.internalChordEngine.modules.settings.internalControlSettingsState import InternalControlSettingsState
from musicEngine.chordEngine.modules.bass.bassState import BassState
from musicEngine.chordEngine.modules.chords.chordsState import ChordsState
from musicEngine.chordEngine.modules.inversion.inversionState import InversionState
from musicEngine.chordEngine.modules.key.keyState import KeyState
from musicEngine.chordEngine.modules.scale.scaleState import ScaleState

class ChordEngineControlMode(Enum):
    INTERNAL = 'internal'
    EXTERNAL = 'external'

class ExternalChordScaleMode(Enum):
    LAST_SEVEN = 1
    STATISTICAL_LAST_SEVEN = 2
    PREFERED_VECTOR_DISTANCE = 3


class ExternalChordMode(Enum):
    MOST_RECENT_NOTE_SET = 1
    STATISTICAL = 2


class ExternalRootMode(Enum):
    LOWEST = 1


class ChordEngineState():

    scale: ScaleState = ScaleState()
    key: KeyState = KeyState()
    inversion: InversionState = InversionState()
    bassPosition: InversionState = InversionState()
    chord: ChordsState = ChordsState()
    bass: BassState = BassState()
    chordOctave: int = 0
    spread: int = SPREAD_STEPS_PER_OCTAVE
    voiceCount: int = 4
    hold: bool = False

    #Internal Chord Engine State
    modulation: ModulationsState = ModulationsState()
    secondary: SecondariesState = SecondariesState()
    alternate: bool = False
    internalSettings: InternalControlSettingsState = InternalControlSettingsState()

    #External Chord Engine State
    noteInHistory: NoteHistoryState = NoteHistoryState()
    scaleMode: ExternalChordScaleMode = ExternalChordScaleMode.LAST_SEVEN
    chordMode: ExternalChordMode = ExternalChordMode.MOST_RECENT_NOTE_SET
    rootMode: ExternalRootMode = ExternalRootMode.LOWEST
    preferredScaleClasses: List[List[int]] = [[0, 2, 4, 5, 7, 9, 11], [0, 2, 4, 6, 7, 9, 10]]


state = ChordEngineState()