# Bugs Fixed During Test Implementation

## Bug 1: Inversion.set_range() re-entrancy resets range value

**File:** `music_engine/chord_engine/modules/inversion/__init__.py:69-71`

**Symptom:** Calling `set_range(6)` when the current range is 4 silently resets the range back to 4.

**Root Cause:** `set_range()` dispatched `update_redux_value()` before `update_redux_range()`. The value dispatch triggered the Redux store subscriber (`handle_store_update`), which saw that `store.inversionRange (4) != state.inversion.range (6)` and called `self.set_range(4)`, undoing the change before the range dispatch could fire.

**Fix:** Swapped dispatch order — `update_redux_range()` now fires before `update_redux_value()`, ensuring the store has the correct range before any subscriber re-entrance.

**Impact:** This bug was latent in production because `set_range` is typically called *from* the store subscriber (where the store already has the correct range), but would affect any direct `set_range()` call with a delta > 1.

---

## Bug 2: Aftertouch and CC values can exceed MIDI range (128 instead of 127)

**File:** `music_engine/midi/__init__.py:194, 199`

**Symptom:** When the controller joystick is at maximum position (`value=1.0`), the aftertouch and CC values sent to MIDI are 128, which exceeds the valid MIDI data byte range of 0-127.

**Root Cause:** The conversion formula `math.floor(((value+1)/2)*128)` produces 128 for `value=1.0`: `floor((2/2)*128) = floor(128) = 128`.

**Fix:** Added `min(..., 127)` clamp: `min(math.floor(((value+1)/2)*128), 127)`.

**Impact:** MIDI data bytes are 7-bit (0-127). Sending 128 would set the high bit, potentially being interpreted as a status byte by some MIDI receivers, causing protocol corruption or ignored messages. In practice, most MIDI libraries and hardware may silently mask to 7 bits, but the behavior is undefined by the MIDI spec.

---

## Bug 3: Duplicate chord note incorrectly sets bass note

**File:** `music_engine/midi/__init__.py:346-350`

**Symptom:** If a chord note that is already playing is sent again (duplicate), the bass note state is incorrectly overwritten with that chord note.

**Root Cause:** The `__store_note_on` method used an `if/else` structure:
```python
if player == 'chord' and note not in playingChordNotes:
    playingChordNotes.append(note)
else:
    playingBassNote = note  # BUG: catches duplicate chord notes too!
```
The `else` branch caught three cases: (1) bass notes (correct), (2) duplicate chord notes (bug), and (3) any unknown player type (bug).

**Fix:** Changed to explicit `if/elif` for each player type:
```python
if player == 'chord':
    if note not in playingChordNotes:
        playingChordNotes.append(note)
elif player == 'bass':
    playingBassNote = note
```

**Impact:** In normal operation, duplicate chord notes are unlikely because `chord_button_on` stops the previous chord before playing the new one. However, if timing or async scheduling caused a duplicate note-on, the bass display and bass channel would incorrectly show/play a chord note as bass, and the actual bass note state would be lost.
