# Unit Test Plan for MidiShock3

## Overview

This plan introduces pytest as the test framework and defines a phased approach to achieving comprehensive unit test coverage. The existing `replay_test.py` is an integration test and will remain separate — this plan focuses exclusively on isolated unit tests.

## Current State

- **No pytest** — only `unittest` used in `replay_test.py`
- **No test infrastructure** — no fixtures, conftest, or test helpers
- **Global mutable state** — `chord_engine_state.py` has a module-level `state` singleton shared by all chord engine modules
- **Redux store singleton** — `redux/__init__.py` creates `store` at import time; every module imports and dispatches to it directly
- **Hardware imports at module level** — `evdev`, `rtmidi`, `tkinter` must be mocked before importing anything
- **Side effects on import** — `constants.py` loads JSON files at import time

## Phase 0: Infrastructure Setup

### 0.1 Add pytest and test dependencies

```toml
# pyproject.toml additions
[dependency-groups]
dev = [
    "ruff>=0.15.6",
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

### 0.2 Create test directory structure

```
tests/
├── conftest.py              # Global fixtures (store reset, state reset, hardware mocks)
├── unit/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── test_command_type.py
│   │   └── test_app_parameter.py
│   ├── chord_engine/
│   │   ├── __init__.py
│   │   ├── test_chord.py
│   │   ├── test_dual_chord.py
│   │   ├── test_scale.py
│   │   ├── test_key.py
│   │   ├── test_inversion.py
│   │   ├── test_bass_position.py
│   │   ├── test_chord_octave.py
│   │   ├── test_spread.py
│   │   ├── test_voice_count.py
│   │   ├── test_hold.py
│   │   ├── test_chord_engine_base.py
│   │   ├── test_internal_chord_engine.py
│   │   └── test_external_chord_engine.py
│   ├── controller_coupler/
│   │   ├── __init__.py
│   │   └── test_controller_coupler.py
│   ├── rhythm_engine/
│   │   ├── __init__.py
│   │   └── test_rhythm_engine.py
│   ├── midi/
│   │   ├── __init__.py
│   │   └── test_midi.py
│   ├── redux/
│   │   ├── __init__.py
│   │   ├── test_reducers.py
│   │   └── test_settings_storage.py
│   └── controller_manager/
│       ├── __init__.py
│       └── test_controller_models.py
└── integration/                # Move existing replay_test.py here later
```

### 0.3 Create `conftest.py` with core fixtures

The conftest needs to handle the three critical test isolation problems:

```python
# tests/conftest.py

import sys
from unittest.mock import MagicMock
import pytest

# Mock hardware modules before any project imports
sys.modules['rtmidi'] = MagicMock()
sys.modules['rtmidi.midiconstants'] = MagicMock()
sys.modules['evdev'] = MagicMock()
sys.modules['tkinter'] = MagicMock()


@pytest.fixture(autouse=True)
def reset_chord_engine_state():
    """Reset the module-level ChordEngineState before each test."""
    from music_engine.chord_engine.chord_engine_state import ChordEngineState
    import music_engine.chord_engine.chord_engine_state as state_module
    state_module.state = ChordEngineState()
    yield
    state_module.state = ChordEngineState()


@pytest.fixture(autouse=True)
def reset_redux_store():
    """Reload the Redux store so each test starts with fresh state."""
    import importlib
    import redux
    importlib.reload(redux)
    yield
```

---

## Phase 1: Pure Logic (No Mocking Required)

These modules contain pure functions that can be tested with just inputs and outputs. Start here for quick wins and to validate the test infrastructure.

### 1.1 `models/command_type.py` — CommandType enum methods

- `CommandType.commands()` returns correct Command lists for each type
- `CommandType.label()` returns human-readable strings

### 1.2 `music_engine/chord_engine/modules/chords/__init__.py` — Chord math

Pure functions that convert scale degrees to MIDI notes:

| Function | What to test |
|----------|-------------|
| `get_note_for_key(note, key)` | Scale degree + key → MIDI note for all 12 keys |
| `find_all_notes(note_degrees)` | Generates all octave variants within MIDI range |
| `__convert_spread(spread)` | Spread parameter → octave offset |
| `__get_chord_from_pattern(pattern, all_notes)` | Pattern application with inversion/spread |
| `get_chord_from_notes(all_notes)` | Full chord voicing pipeline |
| `get_bass_from_notes(all_notes, all_roots)` | Bass note selection with positioning |

**Tests:** Major/minor triads, 7th chords, edge cases at MIDI boundaries (0, 127), various inversions and spreads.

### 1.3 `music_engine/chord_engine/modules/scale/__init__.py` — Scale transposition

| Function | What to test |
|----------|-------------|
| `__find_scale_notes_for_key(key)` | Transposes scale to all 12 keys |
| `__find_scale_notes()` | Precomputes all 12 transpositions |

**Tests:** Major scale in C (no transposition), chromatic scale, pentatonic, verify note wrapping at octave boundary.

### 1.4 `music_engine/chord_engine/modules/inversion/__init__.py` — Analog processing

| Function | What to test |
|----------|-------------|
| `process_value(raw_value)` | Analog input → discrete inversion with hysteresis snap |

**Tests:** Full range sweep (-1 to 1), snap behavior near boundaries, range=0 edge case, various inversion ranges.

### 1.5 `music_engine/chord_engine/external_chord_engine/__init__.py` — Chord recognition

| Function | What to test |
|----------|-------------|
| `get_scale_and_key(note_classes)` | Match note set to known scale |
| `use_notes_as_scale(note_classes)` | Convert arbitrary notes to scale |
| `notes_fit_in_scale(note_classes, scale)` | Subset check |
| `get_prime_form(note_classes)` | Find minimal rotation of pitch class set |
| `rotate_back(r, note_classes)` / `rotate_forward(r, note_classes)` | Pitch class rotation |

**Tests:** Common chord types (major, minor, dim, aug, 7ths), chromatic edge cases, empty input.

### 1.6 `music_engine/rhythm_engine/__init__.py` — Interval generation

| Function | What to test |
|----------|-------------|
| `__get_regular_intervals(n)` | Arithmetic sequence of strum intervals |
| `__get_random_intervals(n)` | Normal distribution intervals (seed numpy for determinism) |

**Tests:** n=1 (single note, no strum), n=4 (standard chord), n=0 edge case, verify intervals sum correctly.

---

## Phase 2: State-Dependent Modules (Requires State Fixture)

These modules read/write the module-level `state` object and dispatch to the Redux store. Tests need the `reset_chord_engine_state` and `reset_redux_store` fixtures from conftest.

### 2.1 Chord Engine Modules — Shared Pattern

All of these follow the same pattern: constructor takes `(type, update_chord_engine)`, subscribes to store, provides `get_parameters()`. Test each with a mock `update_chord_engine` callback.

| Module | Key behaviors to test |
|--------|----------------------|
| **Key** | `set()` normalizes to 0-11 via modulo; `increment()`/`decrement()` use configurable step; dispatches to Redux; calls `update_chord_engine` on change |
| **Spread** | `set()` clamps to `[1, MAX_SPREAD_OCTAVES * SPREAD_STEPS_PER_OCTAVE]`; increment/decrement; Redux sync |
| **VoiceCount** | `set()` clamps to `[1, MAX_VOICE_COUNT]`; increment/decrement; Redux sync |
| **ChordOctave** | `apply(notes)` shifts all notes by octave offset; clamp to MIDI range; Redux sync |
| **Hold** | `toggle()` flips state; calls `stop_chord_and_bass` when disabling; Redux sync |
| **ChordInversion** | `set_value()` clamps to range; `set_range()` re-clamps value; `set_analog_value()` uses `process_value()`; `toggle_lock()` |
| **BassPosition** | Same as ChordInversion but for bass voice |

**Test pattern for each:**
```python
def test_key_set_wraps_around():
    key = Key(AppParameterType.INTERNAL_CHORD_ENGINE, mock_callback)
    key.set(14)
    assert state.key.value == 2  # 14 % 12

def test_key_increment_calls_update():
    mock = MagicMock()
    key = Key(AppParameterType.INTERNAL_CHORD_ENGINE, mock)
    key.increment()
    mock.assert_called()
```

### 2.2 `DualChord` — Chord selection

- Returns main chord when `state.alternate` is False
- Returns alternate chord when `state.alternate` is True
- Correctly delegates to underlying Chord objects
- Handles secondary chords

### 2.3 Redux Reducers

Each reducer in `redux/reducers/` is a pure function `(state, action) → new_state`. These are trivially testable:

| Reducer | Actions to test |
|---------|----------------|
| `music_engine` | `change_key`, `change_scale`, `change_spread`, `change_voice_count`, `change_chord_octave`, `change_inversion_*`, `change_bass_position_*`, `change_chord_type`, `change_strum_*`, `change_velocity_*`, `change_midi_*` |
| `controller_coupler` | `update_control_map`, `add_app_parameters`, `update_controls` |
| `controller_manager` | `add_controller`, `remove_controller` |
| `display` | `change_frame` |

**Test pattern:**
```python
def test_change_key_action():
    state = reducer(undefined, {"type": "INIT"})
    new_state = reducer(state, change_key(5))
    assert new_state["key"] == 5
```

---

## Phase 3: Component-Level Tests (Requires Mocking)

These test larger components in isolation by mocking their dependencies.

### 3.1 `ControllerCoupler` — Event routing

**What to mock:** Redux store (use fixture), AppParameters (use real objects with mock callbacks)

**Tests:**
- `event_handler()` routes ControlEvent to correct AppParameter callback
- Unknown control keys are silently dropped
- `ChordEngineControlMode` filtering: INTERNAL parameters ignored in EXTERNAL mode and vice versa
- `process_new_parameters()` generates INCREMENT_/DECREMENT_ wrapper parameters
- `__map_control_event_to_parameter_event()` maps all MappableControlEvent types correctly

### 3.2 `ChordEngine` (base class via InternalChordEngine)

**What to mock:** `send_message` (to capture ChordEngineMessages without needing RhythmEngine)

**Tests:**
- `chord_button_on(button)` → sends ON message with correct notes
- `chord_button_off(button)` → sends OFF message
- Button queue: pressing A then B plays B; releasing B returns to A
- `hold` mode: releasing button does NOT send OFF
- `stop_chord_and_bass()` sends OFF for both chord and bass
- `update_chord_from_control_state()` replays current chord after parameter change

### 3.3 `InternalChordEngine` — Preset loading

**What to mock:** `send_message`

**Tests:**
- `load_setting(index)` correctly parses preset chords, scale, modulations, secondaries
- `increment_setting()` / `decrement_setting()` cycle through SETTINGS array (with wrapping)
- `get_chord_notes(button)` returns correct notes for each button in a known preset
- Modulation application changes chord output
- Secondary chords layer correctly

### 3.4 `ExternalChordEngine` — Chord recognition pipeline

**What to mock:** `send_message`, asyncio (use `pytest-asyncio`)

**Tests:**
- `process_queue()` with known MIDI input produces expected chord
- `determine_chord_and_scale()` correctly identifies major/minor/7th chords
- Scale detection from note history
- Queue is thread-safe (concurrent `handle_midi_message` calls)

### 3.5 `RhythmEngine` — Note scheduling

**What to mock:** `asyncio.create_task`, callbacks

**Tests:**
- `handle_message(ON)` with strum_interval=0 sends all notes immediately
- `handle_message(ON)` with strum_interval>0 schedules notes with correct delays
- `handle_message(OFF)` cancels pending notes and sends all note-offs
- Bass on/off are always immediate (no strum)
- Strum mode changes (regular vs random) produce different interval patterns
- Generation counter prevents stale scheduled notes from firing

### 3.6 `Midi` — MIDI state management

**What to mock:** `rtmidi.MidiIn`, `rtmidi.MidiOut`

**Tests:**
- `__note_on()` sends correct MIDI bytes `[NOTE_ON | channel, note, velocity]`
- `__note_off()` sends correct MIDI bytes
- Channel distribution: notes spread across channels when `channel_count > 1`
- `__store_note_on()` / `__store_note_off()` correctly track active notes
- Aftertouch conversion: analog -1..1 → 0..127
- CC value sending only when changed
- `handle_midi_in()` correctly parses NOTE_ON (velocity > 0) vs NOTE_OFF (velocity = 0)

### 3.7 `SettingsStorageUtility` — File I/O

**What to mock:** File system (use `tmp_path` fixture)

**Tests:**
- `save_settings()` writes valid JSON
- `load_settings()` reads and applies settings to Redux store
- Missing file handled gracefully
- Corrupt JSON handled gracefully

---

## Phase 4: Controller Manager Models

The controller manager has hardware dependencies (`evdev`), but its **models** are pure data classes that can be tested.

### 4.1 Controller Models

| Model | Tests |
|-------|-------|
| `ControlEvent` | Construction, field access |
| `RawControlEvent` | Enum values |
| `MappableControlEvent` | Enum values |
| `MappableControlType` | Enum values |
| `RawControlType` | Enum values |
| Controller config models | `get_mappable_control_event()`, `get_mappable_control_keys()` |

### 4.2 Control Map

- `default_control_map` maps all expected DualShock4 controls
- Control map lookup returns correct parameter keys

---

## Required Refactoring

### R1: Extract pure logic from `Chord` class (Phase 1 prerequisite)

Several methods in `Chord.__init__.py` are private but contain testable pure logic. Options:

**Option A (preferred): Test via public methods.** The public methods `get_chord()`, `get_bass()` call the private methods internally. Construct a `Chord` object with known inputs and verify outputs. No code changes needed.

**Option B: Make helper functions module-level.** Move `get_note_for_key()`, `find_all_notes()` out of the class since they don't use `self`. This is a minor refactor but makes them directly importable for testing.

**Recommendation:** Start with Option A. Only refactor if tests become unwieldy.

### R2: Make `Scale` methods testable (Phase 1 prerequisite)

`__find_scale_notes_for_key()` and `__find_scale_notes()` are name-mangled private methods. Options:

**Option A (preferred): Test via `Scale.get()`.** Construct Scale, call `update()` with a known scale, verify `get()` for each key.

**Option B:** Rename to single-underscore `_find_scale_notes_for_key()` to allow test access without name mangling. Minor refactor.

**Recommendation:** Start with Option A.

### R3: Settings storage path injection (Phase 3 prerequisite)

`SettingsStorageUtility` hardcodes the file path from `constants.py`. To test file I/O:

- Add an optional `path` parameter to `__init__` or `load_settings()`
- Tests pass a `tmp_path` fixture path
- Default behavior unchanged

### R4: RhythmEngine async testability (Phase 3 prerequisite)

`RhythmEngine.__schedule_message()` creates asyncio tasks directly. For unit testing:

- Use `pytest-asyncio` with a real event loop for schedule/cancel tests
- OR mock `asyncio.create_task` to capture scheduled coroutines and run them synchronously

**Recommendation:** Use `pytest-asyncio`. It handles event loop setup and is the standard approach.

---

## What NOT to Unit Test (Save for Integration Tests)

- **Controller hardware detection** (`Controller.check_for_new_connections`) — requires evdev
- **MIDI port enumeration** (`Midi.start()`, `__reconnect()`) — requires rtmidi hardware
- **Display rendering** — requires tkinter
- **Full event pipeline** (controller → coupler → engine → rhythm → MIDI) — already covered by `replay_test.py`
- **Threading behavior** in Controller's device read threads
- **App startup orchestration** (`app.py`) — integration concern

---

## Execution Order

| Step | What | Estimated Tests | Depends On |
|------|------|----------------|------------|
| 0 | Infrastructure (pytest, conftest, directory) | 0 | — |
| 1.1 | CommandType | ~8 | Step 0 |
| 1.2 | Chord math | ~25 | Step 0 |
| 1.3 | Scale transposition | ~10 | Step 0 |
| 1.4 | Inversion analog processing | ~10 | Step 0 |
| 1.5 | External chord recognition (pure) | ~15 | Step 0 |
| 1.6 | Rhythm interval generation | ~8 | Step 0 |
| 2.1 | Chord engine modules (Key, Spread, etc.) | ~40 | Step 0 |
| 2.2 | DualChord | ~8 | Step 0 |
| 2.3 | Redux reducers | ~30 | Step 0 |
| 3.1 | ControllerCoupler | ~15 | Steps 2.1, 2.3 |
| 3.2 | ChordEngine base | ~15 | Steps 1.2, 2.1 |
| 3.3 | InternalChordEngine | ~12 | Step 3.2 |
| 3.4 | ExternalChordEngine | ~10 | Steps 1.5, 3.2 |
| 3.5 | RhythmEngine | ~12 | R4 |
| 3.6 | Midi | ~15 | Step 0 |
| 3.7 | SettingsStorage | ~6 | R3 |
| 4.1 | Controller models | ~10 | Step 0 |
| 4.2 | Control map | ~5 | Step 0 |
| | **Total** | **~244** | |

---

## Key Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Module-level `state` object causes test pollution | `autouse` fixture resets it before every test |
| Redux store retains state between tests | `autouse` fixture reloads the module |
| `constants.py` JSON loading fails in test env | Hardware mocks in conftest prevent import errors; JSON files exist in repo |
| Private method name mangling blocks testing | Test through public API; refactor to single-underscore only if needed |
| `asyncio` tests are flaky | Use `pytest-asyncio` with proper event loop fixtures; avoid real timing |
