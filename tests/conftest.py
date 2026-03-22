import sys
from unittest.mock import MagicMock, patch

import pytest

# Mock hardware-dependent modules before any project imports.
# These must be set before importing anything from the project tree.
sys.modules["rtmidi"] = MagicMock()

# rtmidi.midiconstants must provide real MIDI constant values since
# the Midi class uses them for byte construction via wildcard import.
_midi_constants = MagicMock()
_midi_constants.NOTE_ON = 0x90
_midi_constants.NOTE_OFF = 0x80
_midi_constants.CHANNEL_PRESSURE = 0xD0
_midi_constants.POLY_AFTERTOUCH = 0xA0
_midi_constants.CONTROL_CHANGE = 0xB0
sys.modules["rtmidi.midiconstants"] = _midi_constants

sys.modules["evdev"] = MagicMock()
sys.modules["PIL"] = MagicMock()
sys.modules["PIL.Image"] = MagicMock()
sys.modules["PIL.ImageTk"] = MagicMock()
sys.modules["music21"] = MagicMock()
sys.modules["music21.chord"] = MagicMock()

# Tkinter stub: real classes that support inheritance so display widget
# tests can verify Python-level attribute state and method behavior.
_tk_item_counter = 0


def _next_item_id():
    global _tk_item_counter
    _tk_item_counter += 1
    return _tk_item_counter


class _WidgetStub:
    """Base stub for all tkinter widgets."""
    def __init__(self, *args, **kwargs):
        pass
    def pack(self, *args, **kwargs): pass
    def grid(self, *args, **kwargs): pass
    def place(self, *args, **kwargs): pass
    def after(self, *args, **kwargs): pass
    def configure(self, *args, **kwargs): pass
    def config(self, *args, **kwargs): pass
    def bind(self, *args, **kwargs): pass
    def tkraise(self, *args, **kwargs): pass
    def destroy(self, *args, **kwargs): pass
    def winfo_children(self): return []


class _CanvasStub(_WidgetStub):
    def create_line(self, *args, **kwargs): return _next_item_id()
    def create_oval(self, *args, **kwargs): return _next_item_id()
    def create_text(self, *args, **kwargs): return _next_item_id()
    def create_rectangle(self, *args, **kwargs): return _next_item_id()
    def create_arc(self, *args, **kwargs): return _next_item_id()
    def create_polygon(self, *args, **kwargs): return _next_item_id()
    def create_image(self, *args, **kwargs): return _next_item_id()
    def coords(self, *args, **kwargs): pass
    def itemconfigure(self, *args, **kwargs): pass
    def itemconfig(self, *args, **kwargs): pass
    def delete(self, *args, **kwargs): pass
    def tag_raise(self, *args, **kwargs): pass


class _TkStub(_WidgetStub):
    def overrideredirect(self, *a): pass
    def attributes(self, *a, **kw): pass
    def wm_attributes(self, *a, **kw): pass
    def focus_set(self): pass
    def geometry(self, *a): pass
    def mainloop(self): pass
    def update(self): pass
    def update_idletasks(self): pass
    def __setitem__(self, key, value): pass


class _ScaleStub(_WidgetStub):
    def get(self): return 0
    def set(self, value): pass


class _DoubleVarStub:
    def __init__(self, *args, **kwargs):
        self._value = kwargs.get("value", 0.0)
    def get(self): return self._value
    def set(self, value): self._value = value


_tk_mock = MagicMock()
_tk_mock.Canvas = _CanvasStub
_tk_mock.Frame = _WidgetStub
_tk_mock.Label = _WidgetStub
_tk_mock.Button = _WidgetStub
_tk_mock.Scale = _ScaleStub
_tk_mock.Tk = _TkStub
_tk_mock.DoubleVar = _DoubleVarStub
_tk_mock.BOTH = "both"
_tk_mock.LEFT = "left"
_tk_mock.RIGHT = "right"
_tk_mock.TOP = "top"
_tk_mock.BOTTOM = "bottom"
_tk_mock.DISABLED = "disabled"
_tk_mock.NORMAL = "normal"
_tk_mock.NW = "nw"
_tk_mock.HORIZONTAL = "horizontal"
sys.modules["tkinter"] = _tk_mock


@pytest.fixture(autouse=True)
def _reset_chord_engine_state():
    """Reset the module-level ChordEngineState in-place before each test.

    We must modify the EXISTING object rather than replacing it, because every
    chord engine module holds its own import reference to the original object
    (via ``from ..chord_engine_state import state``).

    Many state classes use class-level mutable defaults (e.g. ``button_queue: list = []``),
    so we must explicitly set instance-level attributes to shadow them.
    """
    import music_engine.chord_engine.chord_engine_state as state_module
    from constants import SPREAD_STEPS_PER_OCTAVE
    from music_engine.chord_engine.chord_engine_state import (
        ExternalChordMode,
        ExternalChordScaleMode,
        ExternalRootMode,
    )
    from music_engine.chord_engine.state.chords_state import ChordButton
    from music_engine.chord_engine.state.modulations_state import ModulationSide
    from music_engine.chord_engine.state.secondaries_state import SecondarySide

    state = state_module.state

    # Key state
    state.key.value = 0
    state.key.increment_by = 1

    # Scale state — populate note_class_map so Scale.get() works even when
    # Scale hasn't been explicitly initialized (store subscribers from prior
    # tests may call it)
    from music_engine.chord_engine.utils import find_all_octaves_in_range

    chromatic = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    state.scale.key_agnostic = chromatic
    state.scale.note_class_map = {}
    state.scale.all_notes_map = {}
    for key in range(12):
        transposed = [(n + key) % 12 for n in chromatic]
        state.scale.note_class_map[key] = transposed
        state.scale.all_notes_map[key] = find_all_octaves_in_range(transposed)

    # Inversion state
    state.inversion.value = 0
    state.inversion.range = 4
    state.inversion.locked = False

    # Bass position state
    state.bass_position.value = 0
    state.bass_position.range = 4
    state.bass_position.locked = False

    # Chords state — must set instance attrs to shadow class-level mutable defaults
    state.chord.root_class = 0
    state.chord.note_classes = []
    state.chord.playing_notes = []
    state.chord.is_playing = False
    state.chord.active_button = ChordButton.SOUTH
    state.chord.button_queue = []

    # Bass state
    state.bass.playing_note = None
    state.bass.is_playing = False

    # Scalar state
    state.chord_octave = 0
    state.spread = SPREAD_STEPS_PER_OCTAVE
    state.voice_count = 4
    state.hold = False

    # Internal chord engine state
    state.modulation.side = ModulationSide.NONE
    state.modulation.button_queue = []
    state.secondary.side = SecondarySide.NONE
    state.secondary.button_queue = []
    state.alternate = False
    state.internal_settings.index = 0
    state.internal_settings.loading = False

    # External chord engine state
    state.note_in_history.notesPlayed = []
    state.note_in_history.classesPlayed = []
    state.note_in_history.lastContiguous = []
    state.note_in_history.lastContiguousClasses = []
    state.note_in_history.classRecencyRanking = []
    state.note_in_history.lowest_in_contiguous_classes = 127
    state.note_in_history.all = {}
    state.note_in_history.memory_length = 120.0
    state.scale_mode = ExternalChordScaleMode.LAST_SEVEN
    state.chord_mode = ExternalChordMode.MOST_RECENT_NOTE_SET
    state.root_mode = ExternalRootMode.LOWEST
    state.preferred_scale_classes = [[0, 2, 4, 5, 7, 9, 11], [0, 2, 4, 6, 7, 9, 10]]
    state.extension_ranking = [0, 4, 3, 7, 11, 10, 2, 5, 9, 8, 1, 6]
    state.avoid_interval = [6]

    return


@pytest.fixture(autouse=True)
def _reset_redux_store():
    """Reset the Redux store to its initial state before each test.

    Without this, store subscribers and state from prior tests leak across
    test boundaries, causing ordering-dependent failures.

    We create a fresh store and copy its internal closures into the existing
    store object so that all modules holding a reference to the original
    store (via ``from redux import store``) automatically see the reset.
    """
    import pydux

    import redux

    fresh_store = pydux.create_store(redux.reducer)
    redux.store.update(fresh_store)  # type: ignore[unresolved-attribute]
    return


@pytest.fixture(autouse=True)
def _mock_save_settings():
    """Prevent settings from being written to disk during tests."""
    with patch("redux.settings_storage.settings_storage_utility.save_settings"):
        yield
