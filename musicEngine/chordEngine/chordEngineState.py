from enum import Enum
from typing import List
from constants import SPREAD_STEPS_PER_OCTAVE
from musicEngine.chordEngine.state.noteHistoryState import NoteHistoryState
from musicEngine.chordEngine.state.modulationsState import ModulationsState
from musicEngine.chordEngine.state.secondariesState import SecondariesState
from musicEngine.chordEngine.state.internalControlSettingsState import InternalControlSettingsState
from musicEngine.chordEngine.state.bassState import BassState
from musicEngine.chordEngine.state.chordsState import ChordsState
from musicEngine.chordEngine.state.inversionState import InversionState
from musicEngine.chordEngine.state.keyState import KeyState
from musicEngine.chordEngine.state.scaleState import ScaleState


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
    extensionRanking: List[int] = [0, 4, 3, 7, 11, 10, 2, 5, 9, 8, 1, 6]
    avoidInterval: List[int] = [6]


state = ChordEngineState()