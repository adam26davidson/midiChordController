---
name: pi-testing
description: Pi testing and simulation reference — controller events, UI coordinates, touch testing, functional tests, and remote control usage.
user_invocable: true
---

# Pi Testing & Simulation Reference

Use this skill when testing the MidiChordController app running on the Raspberry Pi. It covers controller event simulation, UI touch coordinates, functional testing, and MIDI verification.

## Screenshots & Remote Control

```bash
./tools/test/pi_screenshot.sh                           # Timestamped screenshot saved to /tmp/
./tools/test/pi_record.sh --frames 10 --interval 100    # Capture frames, output as grid (--no-grid for individual files)
./tools/test/pi_send_event.sh press SOUTH_BUTTON        # Simulate a button press (ON + delay + OFF)
./tools/test/pi_send_event.sh analog GYRO_PITCH 0.5     # Simulate an analog input
./tools/test/pi_send_event.sh event SOUTH_BUTTON ON     # Send a single raw event
./tools/test/pi_send_event.sh midi --types note_on,note_off  # Query MIDI output history
./tools/test/pi_send_event.sh midi_in note_on 60 100    # Send MIDI input (for external chord engine)
./tools/test/pi_send_event.sh reset                     # Release all buttons, zero all analogs
./tools/test/pi_touch.sh --tap 400,240                  # Simulate tap, return annotated screenshot
./tools/test/pi_touch.sh --from 200,300 --to 600,100    # Simulate drag, return annotated screenshot
python3 tools/test/run_sequence.py '[...]'               # Run a multi-step test sequence (JSON)
```

**Remote control**: The app starts with `--remote-control` (a TCP server on port 9999) that accepts JSON-encoded controller events and MIDI history queries. `pi_send_event.sh` sends events directly over the network. **Important**: disconnect the physical game controller when testing via remote control — the gyroscope and joysticks continuously stream analog events that will interfere with values set remotely.

## Controller Event Types

Physical controls emit multiple event types with distinct control keys. Understanding these distinctions is important when simulating input via the remote control:

- **Buttons** (e.g. `SOUTH_BUTTON`, `RIGHT_BUMPER`): Emit `ON`/`OFF` events. Map to chord triggers, toggles, etc.
- **Analog axes** (e.g. `DPAD_Y`, `LEFT_STICK_X_POLAR`, `GYRO_PITCH`): Emit `UPDATE` events with a float value, or `POSITIVE`/`NEGATIVE` for directional changes. Map to continuous parameters like octave, spread, inversion.
- **Directional sub-events** (e.g. `DPAD_Y_UP`, `LEFT_STICK_X_RIGHT`): Emit `ON`/`OFF` when an axis crosses a threshold. Map to UI navigation and display-only events.

A single physical control often generates **both** an analog event and directional sub-events. For example, pressing DPAD up on a physical controller sends:
- `DPAD_Y` with `NEGATIVE` → maps to `INTERNAL_OCTAVE` (changes octave, triggers settings save)
- `DPAD_Y_UP` with `ON` → maps to `UI_DPAD_UP` (display-only, no side effects)

When simulating input via remote control, choose the right control key for the intended effect. Use the analog key (e.g. `DPAD_Y NEGATIVE`) to trigger the actual parameter change, or the directional key (e.g. `DPAD_Y_UP ON`) for UI-only effects.

### All Control Keys

- **Buttons**: `SOUTH_BUTTON`, `WEST_BUTTON`, `NORTH_BUTTON`, `EAST_BUTTON`, `RIGHT_BUMPER`, `LEFT_BUMPER`, `RIGHT_TRIGGER`, `LEFT_TRIGGER`, `LEFT_OPTION`, `RIGHT_OPTION`, `START_BUTTON`, `RIGHT_STICK_BUTTON`, `LEFT_STICK_BUTTON`
- **Analog**: `GYRO_PITCH` (inversion), `GYRO_ROLL` (aftertouch), `RIGHT_STICK_X_POLAR` (spread), `RIGHT_STICK_Y_POLAR` (key), `LEFT_STICK_X_POLAR` (voice count), `LEFT_STICK_Y_POLAR` (octave), `TOUCHPAD_X` (bass position)
- **Directional**: `DPAD_Y` POSITIVE/NEGATIVE (octave), `DPAD_X_LEFT`/`DPAD_X_RIGHT` (secondaries)

## Functional Testing

Functional test sequences live in `test/functional/` as JSON files organized by feature area. Run them after making changes to verify things still work:

```bash
python3 tools/test/run_sequence.py test/functional/01_chord_triggering/01_basic_on_off.json
python3 tools/test/run_sequence.py test/functional/08_hold/01_hold_sustain.json -o /tmp/my_test
```

Each test file contains `name`, `description`, `steps` (the sequence), and `assertions` (what to verify in the results). The runner produces screenshots, MIDI history, and touch annotations in an output directory.

For quick inline tests during development, pass a JSON array directly:
```bash
python3 tools/test/run_sequence.py '[{"reset": true}, {"press": "SOUTH_BUTTON"}, {"delay": 200}, {"screenshot": "result"}, {"midi": {"types": ["note_on"]}}]'
```

Available step types: `event`, `press`, `analog`, `midi_in`, `delay`, `screenshot`, `record`, `midi`, `reset`, `touch_tap`, `touch_drag`.

Review results by checking:
- **Screenshots** — visual state at key moments
- **MIDI history** — note_on/off events, velocities, channels, timestamps
- **Touch annotations** — red crosshair/line confirming touch targets were hit (test validity)

## UI Touch Testing Guide

The display is 800x480px. Touch simulation uses `xdotool` with absolute screen coordinates (not window-relative). Use `pi_touch.sh` for taps/drags and `pi_screenshot.sh` to verify results.

**Main menu** (opened via `press START_BUTTON`):

| Button | Coordinates | Notes |
|--------|-------------|-------|
| MIDI | (400, 96) | |
| STRUM | (176, 240) | |
| PERFORM | (400, 240) | Selected by default |
| PATCHES | (624, 240) | Disabled/greyed out |
| CHORD | (400, 384) | |

**◄ MENU back button**: (55, 30) — returns from any settings page to the main menu.

**MIDI Settings page controls:**

| Control | Coordinates | Type |
|---------|-------------|------|
| distribute channels YES | (55, 160) | Toggle button |
| distribute channels NO | (150, 160) | Toggle button |
| chord ch ◄ | (280, 155) | Arrow (disabled when distribute=YES) |
| chord ch ► | (390, 155) | Arrow (disabled when distribute=YES) |
| bass ch ◄ | (510, 155) | Arrow |
| bass ch ► | (630, 155) | Arrow |
| velocity mode CONST | (55, 280) | Toggle button |
| velocity mode RAND | (150, 280) | Toggle button |
| velocity slider | y=280, drag x: 300–750 | Slider |
| velocity deviation slider | y=370, drag x: 300–570 | Slider (disabled when CONST) |
| aftertouch mode CHAN | (40, 400) | Toggle button |
| aftertouch mode POLY | (150, 400) | Toggle button |

**CHORD Settings page controls:**

| Control | Coordinates | Type |
|---------|-------------|------|
| transpose increment ◄ | (55, 130) | Arrow |
| transpose increment ► | (190, 130) | Arrow |
| inversion range ◄ | (285, 130) | Arrow |
| inversion range ► | (430, 130) | Arrow |
| bass range ◄ | (515, 130) | Arrow |
| bass range ► | (650, 130) | Arrow |
| control mode INT | (55, 265) | Toggle button |
| control mode EXT | (150, 265) | Toggle button |

**STRUM Settings page controls:**

| Control | Coordinates | Type |
|---------|-------------|------|
| strum mode RAND | (55, 135) | Toggle button |
| strum mode REG | (150, 135) | Toggle button |
| strum mode OFF | (245, 135) | Toggle button |
| strum order UP | (360, 135) | Toggle (disabled when OFF) |
| strum order DOWN | (450, 135) | Toggle (disabled when OFF) |
| strum order RAND | (540, 135) | Toggle (disabled when OFF) |
| strum interval slider | y=265, drag x: 130–570 | Slider (disabled when OFF) |

**Tips for touch simulation:**
- Sliders: drag on the track itself (exact y matters, ±5px). The slider thumb is the visual indicator — drag from its position.
- Arrow buttons (NumberPicker): small hit targets (~30px wide). Tap directly on the ► / ◄ glyph.
- Toggle buttons: larger hit targets (~80px wide). Easy to hit.
- Disabled controls correctly reject clicks — no need to guard against accidental taps.
- After changing settings, verify with a screenshot. Settings auto-save to `userSettings.json`.
