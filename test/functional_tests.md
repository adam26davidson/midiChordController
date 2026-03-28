# Functional Tests

Comprehensive list of testable features organized by feature area. Tests can be executed using the remote control tools (`pi_send_event.sh`, `pi_touch.sh`, `pi_screenshot.sh`, `pi_send_event.sh midi`) and the sequence runner (`run_sequence.py`).

**Important**: Disconnect the physical game controller before running remote control tests. The controller's gyroscope and joysticks continuously stream analog events (especially `GYRO_PITCH` → inversion) which will interfere with values set via remote control, causing unpredictable results.

---

## 1. Chord Triggering (Internal Engine)

### 1.1 Basic Chord On/Off
- [ ] Press SOUTH_BUTTON ON → chord plays, display shows filled notes, MIDI note_on events sent
- [ ] Press SOUTH_BUTTON OFF → chord stops, display shows hollow notes, MIDI note_off events sent for all notes
- [ ] Press WEST_BUTTON → different chord plays (different notes than SOUTH)
- [ ] Press NORTH_BUTTON → different chord plays
- [ ] Press EAST_BUTTON → different chord plays
- [ ] All 4 note_off events match their corresponding note_on events (no stuck notes)

### 1.2 Button Queue (Multi-press)
- [ ] Hold SOUTH_BUTTON, then press WEST_BUTTON → WEST chord plays (SOUTH stops)
- [ ] Release WEST_BUTTON while SOUTH still held → SOUTH chord resumes
- [ ] Release all buttons → silence
- [ ] Rapid button switching: press/release multiple buttons quickly → no stuck notes

### 1.3 Alternate Voicing
- [ ] Hold RIGHT_TRIGGER (ALTERNATE ON) → display shows alternate chord tones
- [ ] Press chord button while ALTERNATE is ON → alternate voicing plays (different notes than main)
- [ ] Release RIGHT_TRIGGER → reverts to main voicing
- [ ] MIDI output confirms different notes between main and alternate

---

## 2. Key / Transpose

### 2.1 Key Changes
- [ ] Send DPAD_Y POSITIVE (or RIGHT_STICK_Y_POLAR increment) → key display changes (e.g., C → C#)
- [ ] Chord notes shift by the transpose increment (default 1 semitone)
- [ ] Key wraps around: incrementing past B returns to C
- [ ] Key wraps backward: decrementing past C returns to B
- [ ] MIDI output shows notes shifted by correct interval

### 2.2 Transpose Increment Setting
- [ ] In CHORD SETTINGS, change transpose increment to 2
- [ ] Key changes now shift by 2 semitones per step
- [ ] Change to 7 (perfect fifth) → key shifts by 7 semitones per step
- [ ] Reset to 1

---

## 3. Inversion

### 3.1 Chord Inversion
- [ ] Send GYRO_PITCH UPDATE 0.5 → inversion changes, chord voicing shifts
- [ ] Inversion display (right side slider) updates to show new position
- [ ] MIDI notes change — same pitch classes but different octave arrangement
- [ ] Send GYRO_PITCH UPDATE 0.0 → returns to default inversion
- [ ] Inversion at max range → further input has no effect (clamped)
- [ ] Inversion at min range → further input has no effect (clamped)

### 3.2 Inversion Lock
- [ ] Press LEFT_OPTION (toggle INVERSION_LOCK) → lock icon appears in status bar
- [ ] While locked: GYRO_PITCH input has no effect on inversion
- [ ] Press LEFT_OPTION again → unlocked, inversion responds again

### 3.3 Inversion Range Setting
- [ ] In CHORD SETTINGS, increase inversion range (4 → 5)
- [ ] More inversion positions available (slider shows more divisions)
- [ ] Decrease inversion range → fewer positions, current value clamped if outside new range

---

## 4. Bass

### 4.1 Bass On/Off
- [ ] Press LEFT_TRIGGER ON → bass note plays, MIDI note_on sent
- [ ] Release LEFT_TRIGGER → bass stops, MIDI note_off sent
- [ ] Bass note is in lower register (around MIDI 42 / F#2)
- [ ] Bass note is from the chord's bass definition

### 4.2 Bass Position
- [ ] Send TOUCHPAD_X UPDATE value → bass position changes
- [ ] Different bass voicing (different octave of bass note)
- [ ] Bass position independent from chord inversion

### 4.3 Bass Range Setting
- [ ] In CHORD SETTINGS, change bass range → more/fewer bass positions available

---

## 5. Spread

### 5.1 Spread Control
- [ ] Send RIGHT_STICK_X_POLAR POSITIVE → spread increases, chord notes more spread out
- [ ] Display shows spread indicator widening
- [ ] MIDI notes span wider range (more octaves between top and bottom)
- [ ] Send RIGHT_STICK_X_POLAR NEGATIVE → spread decreases, compact voicing
- [ ] Spread at 0 → most compact possible voicing
- [ ] Spread at max → widest voicing

---

## 6. Voice Count

### 6.1 Voice Count Control
- [ ] Send LEFT_STICK_X_POLAR POSITIVE → voice count increases
- [ ] Display shows "v:" indicator updating (e.g., v: 4 → v: 5)
- [ ] More MIDI notes sounding in chord
- [ ] Send LEFT_STICK_X_POLAR NEGATIVE → voice count decreases
- [ ] Fewer MIDI notes in chord
- [ ] Voice count 1 → single note plays
- [ ] Voice count at max (10) → 10 notes in chord

---

## 7. Octave

### 7.1 Octave Shift
- [ ] Send DPAD_Y NEGATIVE → octave decrements, "o:" display changes (e.g., o: 0 → o: -1)
- [ ] All chord notes shift down 12 semitones in MIDI output
- [ ] Send DPAD_Y POSITIVE → octave increments
- [ ] Octave at max (+3) → no further increment
- [ ] Octave at min (-3) → no further decrement
- [ ] Notes clamped to playable range (MIDI 21-108) regardless of octave setting

---

## 8. Hold

### 8.1 Hold Mode
- [ ] Press RIGHT_OPTION → hold toggle, hold icon appears in status
- [ ] Press and release chord button → chord sustains after release
- [ ] Press another chord button → new chord replaces held chord
- [ ] Toggle hold OFF while chord sustaining → chord stops immediately
- [ ] Hold applies to bass as well

---

## 9. Modulations

### 9.1 Left Modulation
- [ ] Press LEFT_BUMPER ON → M1 indicator activates on display
- [ ] Chord notes shift according to left modulation map
- [ ] Scale display updates (keyboard strip shows new scale)
- [ ] MIDI output shows modulated notes
- [ ] Release LEFT_BUMPER → returns to unmodulated scale

### 9.2 Right Modulation
- [ ] Press RIGHT_BUMPER ON → M2 indicator activates
- [ ] Different modulation than left (if configured differently in preset)
- [ ] Release → returns to normal

### 9.3 Modulation Animation
- [ ] Use pi_record.sh to capture modulation on/off → chord circle positions animate smoothly (150ms duration)

---

## 10. Secondary Chords

### 10.1 Left Secondary
- [ ] Press DPAD_X_LEFT ON → S1 indicator activates
- [ ] Chord changes to chromatic secondary (different note set)
- [ ] Secondary uses chromatic intervals, not scale degrees
- [ ] Release → returns to diatonic chord

### 10.2 Right Secondary
- [ ] Press DPAD_X_RIGHT ON → S2 indicator activates
- [ ] Different secondary than left

### 10.3 Secondary + Modulation Combination
- [ ] Activate both modulation and secondary simultaneously → secondary respects modulation overrides if defined in preset

---

## 11. Preset / Settings Management

### 11.1 Preset Switching
- [ ] Press RIGHT_STICK_BUTTON → setting display changes to next preset name
- [ ] Chord definitions update (different notes when pressing buttons)
- [ ] Press LEFT_STICK_BUTTON → previous preset
- [ ] Wraps around at beginning/end of preset list

### 11.2 Preset Loading
- [ ] After switching preset: scale, chords, modulations, secondaries all reflect new preset
- [ ] Key resets or maintains depending on preset

---

## 12. Strumming

### 12.1 Strum Mode
- [ ] In STRUM SETTINGS, set mode to REG → notes strum with regular timing
- [ ] MIDI history shows note_on events with sequential timestamps (not simultaneous)
- [ ] Set mode to RAND → notes strum with randomized timing
- [ ] Set mode to OFF → all notes play simultaneously (same timestamp)

### 12.2 Strum Order
- [ ] Set order to UP → lowest note plays first
- [ ] Set order to DOWN → highest note plays first
- [ ] Set order to RAND → random note order

### 12.3 Strum Interval
- [ ] Increase strum interval → longer delay between strummed notes
- [ ] Decrease to minimum → very fast strum
- [ ] Verify via MIDI timestamps

---

## 13. MIDI Output Settings

### 13.1 Velocity
- [ ] In MIDI SETTINGS, set velocity mode to CONST, value to 80
- [ ] All MIDI note_on events have velocity 80
- [ ] Set mode to RAND → velocities vary around center value
- [ ] Adjust velocity deviation → wider/narrower spread of random velocities

### 13.2 Channel Configuration
- [ ] Change chord channel from 1 to 3 → MIDI note_on events on channel 2 (0-indexed)
- [ ] Change bass channel to 2 → bass notes on channel 1
- [ ] Enable distribute channels → each chord note on different channel
- [ ] Chord channel picker disabled when distribute=YES

### 13.3 Aftertouch
- [ ] Send GYRO_ROLL (AFTERTOUCH) analog value → MIDI aftertouch messages sent
- [ ] In channel mode: single aftertouch per channel
- [ ] In poly mode: individual aftertouch per note
- [ ] Verify via MIDI history: check aftertouch/poly_aftertouch events

---

## 14. Display — Perform View

### 14.1 Controller Display
- [ ] Press SOUTH_BUTTON → S button highlights purple on controller diagram
- [ ] Release → S button returns to outline
- [ ] All 4 face buttons show correct highlight
- [ ] Bumpers, triggers, options, dpad all show on/off state
- [ ] Joystick positions update with analog values

### 14.2 Chord Circle Display
- [ ] Chord press → notes change from outline to filled circles
- [ ] Root note shown in purple/magenta
- [ ] Chord notes shown in white
- [ ] Key letter at top updates with key changes
- [ ] 12 positions around circle correspond to chromatic scale

### 14.3 Keyboard Strip
- [ ] Bottom keyboard shows dots for current chord definition
- [ ] Dots brighten/enlarge when chord is playing
- [ ] Notes outside visible range (36-96) shown as arrows at edges
- [ ] Root notes distinguished from other chord tones

### 14.4 Status Indicators
- [ ] "o:" shows current octave (-3 to +3)
- [ ] "v:" shows current voice count (1-10)
- [ ] Lock icon shows when inversion is locked
- [ ] Hold icon shows when hold is active
- [ ] Setting name shows current preset

### 14.5 Inversion Slider
- [ ] Right-side slider shows current inversion position
- [ ] Divisions match inversion range setting
- [ ] Thumb moves with inversion changes

### 14.6 Spread Indicator
- [ ] Bottom spread arrow shows current spread width
- [ ] Widens with spread increase, narrows with decrease

---

## 15. Display — Settings Pages

### 15.1 MIDI Settings Page
- [ ] All toggle buttons clickable (YES/NO, CONST/RAND, CHAN/POLY)
- [ ] Number picker arrows functional (chord ch, bass ch)
- [ ] Velocity slider draggable
- [ ] Velocity deviation slider draggable (disabled when CONST)
- [ ] Channel pickers disabled when distribute=YES
- [ ] ◄ MENU button returns to menu

### 15.2 CHORD Settings Page
- [ ] Transpose increment arrows functional (1-11)
- [ ] Inversion range arrows functional (1-20)
- [ ] Bass range arrows functional (1-15)
- [ ] INT/EXT toggle switches chord engine mode
- [ ] ◄ MENU button returns to menu

### 15.3 STRUM Settings Page
- [ ] RAND/REG/OFF mode buttons functional
- [ ] UP/DOWN/RAND order buttons functional
- [ ] Order buttons + slider disabled when mode=OFF
- [ ] Strum interval slider draggable
- [ ] ◄ MENU button returns to menu

### 15.4 Menu Navigation
- [ ] START_BUTTON opens/closes menu
- [ ] Tap each menu button → enters correct settings page
- [ ] PATCHES button is disabled (greyed out)
- [ ] From any settings page, ◄ MENU returns to menu
- [ ] From menu, tap PERFORM → returns to perform view

---

## 16. Settings Persistence

### 16.1 Save/Load
- [ ] Change a setting (e.g., velocity) → setting persists after app restart
- [ ] Change key, octave, spread, voice count → all persist after restart
- [ ] MIDI channel settings persist
- [ ] Strum settings persist
- [ ] Corrupt/missing userSettings.json → app starts with defaults

---

## 17. External Chord Engine

### 17.1 Mode Switch
- [ ] In CHORD SETTINGS, switch to EXT → display shows "External Control"
- [ ] Internal chord buttons no longer trigger presets
- [ ] MIDI input now drives chord recognition

### 17.2 Chord Recognition (via midi_in)
- [ ] Send MIDI note_on for C, E, G → app recognizes C major
- [ ] Display updates to show recognized chord
- [ ] Voicing/inversion/spread still apply to recognized chord
- [ ] Send note_off for all → chord stops

### 17.3 External + Voicing Controls
- [ ] While external chord playing: inversion, spread, voice_count still affect output
- [ ] Key changes transpose external chord
- [ ] Hold works with external chords

---

## 18. App Lifecycle

### 18.1 Single Instance
- [ ] Start app → lock file created at /tmp/midichordcontroller.lock
- [ ] Attempt second instance → exits with "already running" error
- [ ] Kill app → lock file removed
- [ ] Stale lock (crashed app) → next start cleans up and starts normally

### 18.2 Fullscreen
- [ ] App starts in fullscreen (no taskbar, no title bar)
- [ ] After restart → still fullscreen (retry mechanism)
- [ ] Multiple rapid restarts → all fullscreen

### 18.3 Remote Control Server
- [ ] App started with --remote-control → TCP port 9999 open
- [ ] Controller events accepted and processed
- [ ] MIDI history queries return data
- [ ] MIDI input messages processed
- [ ] Port reuse: restart doesn't fail with "address in use"

---

## 19. State Interaction Edge Cases

### 19.1 Combined Feature Activation
- [ ] Modulation + secondary + alternate all active at once → notes correctly apply all transformations
- [ ] Activate modulation while secondary is active → secondary respects modulation overrides
- [ ] Toggle alternate while modulation active → alternate voicing uses modulated scale

### 19.2 Hold + Button Queue
- [ ] Hold ON, press SOUTH, press WEST, release WEST → SOUTH sustains (hold keeps it)
- [ ] Hold ON, press SOUTH, press WEST, press NORTH, release all → last chord sustains
- [ ] Toggle hold OFF while multi-button queue active → all notes stop immediately

### 19.3 Inversion Lock + Range Change
- [ ] Lock inversion at value +2, change range from 4 to 1 → value clamped to new range
- [ ] Lock inversion, change analog input → value doesn't change
- [ ] Unlock → analog input takes effect again

### 19.4 Chord Playing During Preset Switch
- [ ] Chord playing, switch preset → chord stops immediately, no stuck notes
- [ ] Press same button after preset switch → new preset's chord plays
- [ ] Display updates atomically (no partial/stale data visible)

### 19.5 Mode Switch During Playback
- [ ] Internal chord playing, switch to EXT mode → chord stops, display shows "External Control"
- [ ] Switch back to INT → internal chord engine ready, no stale state
- [ ] External chord playing (via MIDI in), switch to INT → external chord stops

---

## 20. Bass Edge Cases

### 20.1 Bass + Hold
- [ ] Hold ON, chord + bass both playing → release chord button → both sustain
- [ ] Toggle hold OFF → both chord and bass stop

### 20.2 Bass Per Active Button
- [ ] SOUTH active + bass playing → press WEST → bass should use WEST's bass definition
- [ ] Release WEST (SOUTH resumes) → bass uses SOUTH's bass definition again

### 20.3 Bass Position Lock
- [ ] Set bass position to non-zero, toggle lock → analog input has no effect
- [ ] Unlock → bass position responds to input again

### 20.4 Bass + Distribute Channels
- [ ] Distribute channels ON → bass still uses bass channel, chord notes get separate channels
- [ ] Bass channel same as a chord channel → verify no MIDI collision/crash

---

## 21. MIDI Edge Cases

### 21.1 Channel Exhaustion
- [ ] Distribute channels ON, play chord with 10+ voices → channels wrap/reuse correctly
- [ ] All note_off messages go to the correct channel

### 21.2 Channel Change During Playback
- [ ] Chord playing on channel 0, change chord channel to 5 → existing notes stay on 0, new notes on 5
- [ ] Bass playing, change bass channel → similar behavior

### 21.3 Channel Collision
- [ ] Set chord channel = bass channel → both play on same channel without crash
- [ ] Notes still paired correctly (note_on/note_off match)

### 21.4 MIDI Port Disconnect/Reconnect
- [ ] Chord playing, MIDI port disconnects → app doesn't crash, logs warning
- [ ] Port reconnects → MIDI output resumes
- [ ] Port monitoring loop (50ms) detects changes

### 21.5 Velocity/Aftertouch Modes
- [ ] Change velocity mode from RAND to CONST while notes playing → new notes use constant, old unaffected
- [ ] Aftertouch in channel mode → sent to chord channel + bass channel
- [ ] Aftertouch in poly mode → sent per note with correct note number
- [ ] Aftertouch with distribute channels → sent to all occupied channels

---

## 22. Strum Edge Cases

### 22.1 Strum with Voice Count 1
- [ ] Single voice + strum REG → note plays immediately (no delay for 1 note)

### 22.2 Strum Mode Change During Playback
- [ ] Chord playing with strum OFF → change to REG → current chord unaffected, next chord strums

### 22.3 Long Strum Interval + Rapid Presses
- [ ] Strum interval = 0.5s, press SOUTH → notes begin strumming
- [ ] Press WEST at 0.2s (before strum completes) → SOUTH strum cancelled, WEST starts

### 22.4 Strum Order Change During Strum
- [ ] Change strum order while notes are being strummed → in-flight notes unaffected

---

## 23. Controller/Hardware Edge Cases

### 23.1 Controller Disconnect
- [ ] Controller unplugged during chord playback → app doesn't crash
- [ ] Display shows controller disconnected state
- [ ] Reconnect → controller input resumes

### 23.2 Analog Jitter/Drift
- [ ] Joystick near center with slight drift → inversion snap prevents flickering
- [ ] Display doesn't jitter with noisy analog input

### 23.3 Rapid Button Spam
- [ ] Mash chord button rapidly (10+ presses in 1s) → no stuck notes, final state correct
- [ ] No excessive MIDI message backlog

---

## 24. Note Range Clamping

- [ ] Octave +3 with high chord → notes clamped to MIDI 108 max
- [ ] Octave -3 with low chord → notes clamped to MIDI 21 min
- [ ] Bass at extreme positions → clamped to valid range
- [ ] Very high spread + high octave → top notes clamped, bottom notes still valid

---

## 25. Simultaneous Live Changes

- [ ] Change key while chord is playing → chord updates to new key in real time
- [ ] Change inversion while chord is playing → voicing updates live
- [ ] Change spread while chord is playing → note spacing updates
- [ ] Change voice count while chord is playing → note count changes
- [ ] Activate modulation while chord is playing → notes shift to modulated scale
- [ ] Change octave while chord is playing → all notes shift

---

## 26. Regression Tests (Known Bug Patterns)

### 26.1 Parameter Cache Staleness
- [ ] Load preset A, then preset B → modulation parameters use preset B's scale (not A's)

### 26.2 Modulation Scale Immutability
- [ ] Apply modulation → state.scale.key_agnostic unchanged (original scale preserved)
- [ ] Remove modulation → scale returns to original

### 26.3 Settings Write Doesn't Trigger Restart
- [ ] Change octave (writes userSettings.json) → app does NOT restart
- [ ] Change any persisted setting → no restart
