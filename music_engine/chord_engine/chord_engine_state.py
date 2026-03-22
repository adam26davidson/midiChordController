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


class ExternalChordMode(Enum):
    MOST_RECENT_NOTE_SET = 1


class ExternalRootMode(Enum):
    LOWEST = 1



class ChordEngineState:

    def __init__(self) -> None:
        self.scale: ScaleState = ScaleState()
        self.key: KeyState = KeyState()
        self.inversion: InversionState = InversionState()
        self.bass_position: InversionState = InversionState()
        self.chord: ChordsState = ChordsState()
        self.bass: BassState = BassState()
        self.chord_octave: int = 0
        self.spread: int = SPREAD_STEPS_PER_OCTAVE
        self.voice_count: int = 4
        self.hold: bool = False

        # Internal Chord Engine State
        self.modulation: ModulationsState = ModulationsState()
        self.secondary: SecondariesState = SecondariesState()
        self.alternate: bool = False
        self.internal_settings: InternalControlSettingsState = InternalControlSettingsState()

        # External Chord Engine State
        self.note_in_history: NoteHistoryState = NoteHistoryState()
        self.scale_mode: ExternalChordScaleMode = ExternalChordScaleMode.LAST_SEVEN
        self.chord_mode: ExternalChordMode = ExternalChordMode.MOST_RECENT_NOTE_SET
        self.root_mode: ExternalRootMode = ExternalRootMode.LOWEST
        self.preferred_scale_classes: list[list[int]] = [[0, 2, 4, 5, 7, 9, 11], [0, 2, 4, 6, 7, 9, 10]]
        self.extension_ranking: list[int] = [0, 4, 3, 7, 11, 10, 2, 5, 9, 8, 1, 6]
        self.avoid_interval: list[int] = [6]


state = ChordEngineState()
