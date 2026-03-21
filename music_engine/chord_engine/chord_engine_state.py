from enum import Enum

from constants import SPREAD_STEPS_PER_OCTAVE
from music_engine.chord_engine.state.bass_state import BassState
from music_engine.chord_engine.state.chords_state import ChordsState
from music_engine.chord_engine.state.internal_control_settings_state import InternalControlSettingsState
from music_engine.chord_engine.state.inversion_state import InversionState
from music_engine.chord_engine.state.key_state import KeyState
from music_engine.chord_engine.state.modulations_state import ModulationsState
from music_engine.chord_engine.state.note_history_state import NoteHistoryState
from music_engine.chord_engine.state.scale_state import ScaleState
from music_engine.chord_engine.state.secondaries_state import SecondariesState


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
