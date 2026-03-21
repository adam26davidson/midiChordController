# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MidiChordController is a Python GUI application that generates MIDI chords based on game controller input. Designed for Raspberry Pi with Pimoroni HyperPixel (800x480px), it also supports windowed and headless modes. Primary use case: live music performance where a game controller manipulates chord voicings, inversions, and modulations in real time.

## Running the Application

```bash
python3 main.py              # Fullscreen on HyperPixel display
python3 main.py --window     # Windowed mode on another display
python3 main.py --no-display # Headless (no GUI)
```

## Running Tests

No formal test runner is configured. Tests in `test/` are run directly:

```bash
python3 test/music_engine_test.py
python3 test/controller_manager_test.py
python3 test/replay_test.py          # Replays recorded evdev events through the pipeline
```

The `test/` directory also contains debugging/analysis scripts (not tests) for profiling controller event processing against recorded sessions:

```bash
python3 test/analyze_recording.py           # Event rates, button timings, density stats
python3 test/analyze_processing_cost.py     # Coupler throughput: executed vs dropped events
python3 test/analyze_inversion_changes.py   # Gyro→inversion change rate (for tuning snap)
```

These scripts accept an optional path to a `.jsonl` recording file (defaults to `test/evdev_recording.jsonl`).

## Architecture

### Event Flow

```
Game Controller (USB/Bluetooth)
    → ControllerManager  (evdev: detects hardware, emits ControlEvents)
    → ControllerCoupler  (maps ControlEvents → AppParameters → Commands)
    → ChordEngine        (processes commands, builds chord voicings)
    → RhythmEngine       (manages timing/note-on/off, max 10 voices)
    → MIDI Output        (python-rtmidi)
    → Display            (Tkinter GUI subscribes to Redux store)
```

### State Management

Uses **pydux** (Redux-like) with a centralized store (`redux/__init__.py`). Reducers handle: `controllerManager`, `controllerCoupler`, `musicEngine`, `display`. Components subscribe to state changes.

**Important**: State is split between the Redux store (for cross-component concerns like settings and display state) and local state objects within the chord engine modules (e.g., `key_state`, `scale_state`, `inversion_state`). When modifying chord engine internals, update local state objects; use Redux for anything the display or settings UI needs to observe.

### Dual Chord Engine Design

Both engines inherit from `music_engine/chord_engine/chord_engine.py`:

- **InternalChordEngine** (`internal_chord_engine/`): Generates chords from JSON presets (scales, chord definitions, modulations, secondaries).
- **ExternalChordEngine** (`external_chord_engine/`): Recognizes chords from incoming MIDI input, then applies the same voicing/inversion pipeline.

### Parameter System

`AppParameter` (`models/app_parameter.py`) is the central abstraction for any controllable value. Each parameter defines:
- Valid command types (`ANALOG`, `ON_OFF`, `TOGGLE`)
- The function to call on each command
- Whether it can be remapped via the settings UI
- Which engine type it belongs to (`INTERNAL_CHORD_ENGINE`, `EXTERNAL_CHORD_ENGINE`, etc.)

Controller buttons/axes map to AppParameters via `controller_coupler/`. Parameters can be remapped dynamically at runtime.

### Chord System Concepts

- **DualChord**: Each button has a main and alternate voicing, each with its own bass note
- **Scale degree indexing**: Chords defined as arrays of scale degree indices
- **Modulations**: Modal or custom scale transformations per button/mode combo
- **Secondaries**: Chromatic chords layered above diatonic chords, defined per button
- **Inversion**: Note order rearranged by joystick input
- **Spread**: Octave distribution across voices
- **Voice Count**: Number of simultaneous notes

### Settings / Presets

`settings.json` holds an array of presets. Each preset has `name`, `scale`, `modulations`, `chords`, and `secondaries`. The README contains the full schema documentation.

## Key Files

| File | Purpose |
|------|---------|
| `app.py` | Orchestrates startup and wires all subsystems together |
| `main.py` | CLI entry point |
| `constants.py` | Global constants (MIDI ranges, animation timing, display sizes) |
| `redux/__init__.py` | Store initialization with all reducers |
| `music_engine/chord_engine/chord_engine.py` | Abstract base class for both chord engines |
| `controller_coupler/__init__.py` | Maps controller events to parameters and commands |
| `display/__init__.py` | Tkinter GUI, settings UI, performance view |

## Dependencies

- `evdev` — Linux controller input (game controllers via `/dev/input/`)
- `python-rtmidi` — MIDI I/O
- `pydux` + `pyrsistent` — Redux-like state management with immutable data
- `numpy` — Numerical operations for chord/voice math
- `music21` — Music theory utilities
