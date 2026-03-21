from enum import Enum

from constants import SPREAD_STEPS_PER_OCTAVE
from musicEngine.chordEngine.state.bassState import BassState
from musicEngine.chordEngine.state.chordsState import ChordsState
from musicEngine.chordEngine.state.internalControlSettingsState import InternalControlSettingsState
from musicEngine.chordEngine.state.inversionState import InversionState
from musicEngine.chordEngine.state.keyState import KeyState
from musicEngine.chordEngine.state.modulationsState import ModulationsState
from musicEngine.chordEngine.state.noteHistoryState import NoteHistoryState
from musicEngine.chordEngine.state.scaleState import ScaleState
from musicEngine.chordEngine.state.secondariesState import SecondariesState


class ExternalChordScaleMode(Enum):
    LAST_SEVEN = 1
    STATISTICAL_LAST_SEVEN = 2
    PREFERED_VECTOR_DISTANCE = 3


class ExternalChordMode(Enum):
    MOST_RECENT_NOTE_SET = 1
    STATISTICAL = 2


class ExternalRootMode(Enum):
    LOWEST = 1



class ChordEngineState:

    scale: ScaleState = ScaleState()
    key: KeyState = KeyState()
    inversion: InversionState = InversionState()
    bass_position: InversionState = InversionState()
    chord: ChordsState = ChordsState()
    bass: BassState = BassState()
    chord_octave: int = 0
    spread: int = SPREAD_STEPS_PER_OCTAVE
    voice_count: int = 4
    hold: bool = False

    #Internal Chord Engine State
    modulation: ModulationsState = ModulationsState()
    secondary: SecondariesState = SecondariesState()
    alternate: bool = False
    internal_settings: InternalControlSettingsState = InternalControlSettingsState()

    #External Chord Engine State
    note_in_history: NoteHistoryState = NoteHistoryState()
    scale_mode: ExternalChordScaleMode = ExternalChordScaleMode.LAST_SEVEN
    chord_mode: ExternalChordMode = ExternalChordMode.MOST_RECENT_NOTE_SET
    root_mode: ExternalRootMode = ExternalRootMode.LOWEST
    preferred_scale_classes: list[list[int]] = [[0, 2, 4, 5, 7, 9, 11], [0, 2, 4, 6, 7, 9, 10]]
    extension_ranking: list[int] = [0, 4, 3, 7, 11, 10, 2, 5, 9, 8, 1, 6]
    avoid_interval: list[int] = [6]


state = ChordEngineState()
