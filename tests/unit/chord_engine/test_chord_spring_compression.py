"""Tests for chord voicing spring compression behavior.

When inversion pushes notes toward the ceiling of the available note range
(MAX_NOTE=108), the voicing algorithm shifts the entire chord down to fit.
This acts like a spring hitting a wall — the chord compresses rather than
exceeding the bounds.

The mechanism is in Chord.__get_chord_from_pattern() (chords/__init__.py).
"""

import music_engine.chord_engine.chord_engine_state as state_module
from constants import MAX_NOTE, MIN_NOTE, SPREAD_STEPS_PER_OCTAVE
from music_engine.chord_engine.modules.chords import Chord


class TestSpringCompression:
    """Verify that high inversion compresses the chord against the ceiling."""

    def _make_chord(self) -> Chord:
        """Create a C major triad chord for testing."""
        return Chord([0, 4, 7], [0], 0)

    def test_notes_stay_within_all_notes_range(self) -> None:
        """With max inversion, all notes should remain within MIN_NOTE-MAX_NOTE."""
        chord = self._make_chord()
        state_module.state.voice_count = 4
        state_module.state.key.value = 0
        state_module.state.spread = SPREAD_STEPS_PER_OCTAVE
        state_module.state.inversion.value = state_module.state.inversion.range

        result = chord.get_chord()
        for note in result:
            assert MIN_NOTE <= note <= MAX_NOTE, (
                f"Note {note} outside [{MIN_NOTE}, {MAX_NOTE}] at max inversion"
            )

    def test_notes_stay_within_range_at_negative_inversion(self) -> None:
        """With min inversion, all notes should remain within MIN_NOTE-MAX_NOTE."""
        chord = self._make_chord()
        state_module.state.voice_count = 4
        state_module.state.key.value = 0
        state_module.state.spread = SPREAD_STEPS_PER_OCTAVE
        state_module.state.inversion.value = -state_module.state.inversion.range

        result = chord.get_chord()
        for note in result:
            assert MIN_NOTE <= note <= MAX_NOTE, (
                f"Note {note} outside [{MIN_NOTE}, {MAX_NOTE}] at min inversion"
            )

    def test_chord_stops_at_ceiling(self) -> None:
        """Increasing inversion beyond a point should not raise the top note further."""
        chord = self._make_chord()
        state_module.state.voice_count = 4
        state_module.state.key.value = 0
        state_module.state.spread = SPREAD_STEPS_PER_OCTAVE * 2
        state_module.state.inversion.range = 20

        # Sweep inversion upward and track the max note
        max_notes: list[int] = []
        for inv in range(21):
            state_module.state.inversion.value = inv
            result = chord.get_chord()
            max_notes.append(max(result))

        # At some point the max note should stop increasing (hit ceiling)
        final_max = max_notes[-1]
        assert final_max == MAX_NOTE or max_notes.count(final_max) > 1, (
            f"Top note should plateau at ceiling, got max notes: {max_notes[-5:]}"
        )

    def test_chord_stops_at_floor(self) -> None:
        """Decreasing inversion beyond a point should not lower the bottom note further."""
        chord = self._make_chord()
        state_module.state.voice_count = 4
        state_module.state.key.value = 0
        state_module.state.spread = SPREAD_STEPS_PER_OCTAVE * 2
        state_module.state.inversion.range = 20

        # Sweep inversion downward and track the min note
        min_notes: list[int] = []
        for inv in range(0, -21, -1):
            state_module.state.inversion.value = inv
            result = chord.get_chord()
            min_notes.append(min(result))

        # At some point the min note should stop decreasing (hit floor)
        final_min = min_notes[-1]
        assert final_min == MIN_NOTE or min_notes.count(final_min) > 1, (
            f"Bottom note should plateau at floor, got min notes: {min_notes[-5:]}"
        )

    def test_high_voice_count_with_max_inversion_stays_in_range(self) -> None:
        """Even with many voices and max inversion, notes should stay in range."""
        chord = self._make_chord()
        state_module.state.voice_count = 10
        state_module.state.key.value = 0
        state_module.state.spread = SPREAD_STEPS_PER_OCTAVE * 4
        state_module.state.inversion.range = 20
        state_module.state.inversion.value = 20

        result = chord.get_chord()
        for note in result:
            assert MIN_NOTE <= note <= MAX_NOTE, (
                f"Note {note} outside range with 10 voices + max inversion"
            )

    def test_high_voice_count_with_min_inversion_stays_in_range(self) -> None:
        """Even with many voices and min inversion, notes should stay in range."""
        chord = self._make_chord()
        state_module.state.voice_count = 10
        state_module.state.key.value = 0
        state_module.state.spread = SPREAD_STEPS_PER_OCTAVE * 4
        state_module.state.inversion.range = 20
        state_module.state.inversion.value = -20

        result = chord.get_chord()
        for note in result:
            assert MIN_NOTE <= note <= MAX_NOTE, (
                f"Note {note} outside range with 10 voices + min inversion"
            )

    def test_pitch_classes_preserved_across_compression(self) -> None:
        """Compression should not change which pitch classes are present."""
        chord = self._make_chord()
        state_module.state.voice_count = 4
        state_module.state.key.value = 0
        state_module.state.spread = SPREAD_STEPS_PER_OCTAVE * 2

        state_module.state.inversion.value = 0
        pc_center = {n % 12 for n in chord.get_chord()}

        state_module.state.inversion.value = state_module.state.inversion.range
        pc_high = {n % 12 for n in chord.get_chord()}

        assert pc_center == pc_high, (
            f"Pitch classes should be preserved: {pc_center} vs {pc_high}"
        )

    def test_all_keys_stay_in_range_at_extremes(self) -> None:
        """Spring compression should work correctly across all 12 keys."""
        state_module.state.voice_count = 6
        state_module.state.spread = SPREAD_STEPS_PER_OCTAVE * 3
        state_module.state.inversion.range = 10

        for key in range(12):
            state_module.state.key.value = key
            chord = Chord([0, 2, 4, 6], [0], 0, scale=[0, 2, 4, 5, 7, 9, 11])

            for inv in [state_module.state.inversion.range, -state_module.state.inversion.range]:
                state_module.state.inversion.value = inv
                result = chord.get_chord()
                for note in result:
                    assert MIN_NOTE <= note <= MAX_NOTE, (
                        f"key={key} inv={inv}: note {note} outside range"
                    )
