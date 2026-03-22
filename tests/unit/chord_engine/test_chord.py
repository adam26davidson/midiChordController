import music_engine.chord_engine.chord_engine_state as state_module
from music_engine.chord_engine.modules.chords import Chord


class TestChordGetNoteForKey:
    """Test Chord.get_note_for_key — pure scale-degree-to-pitch-class conversion."""

    def test_chromatic_scale_key_c(self):
        chord = Chord([0], [0], 0)  # chromatic scale by default
        assert chord.get_note_for_key(0, 0) == 0  # C
        assert chord.get_note_for_key(4, 0) == 4  # E
        assert chord.get_note_for_key(7, 0) == 7  # G

    def test_chromatic_scale_key_d(self):
        chord = Chord([0], [0], 0)
        # key=2 (D), note 0 → (scale[0] + 2) % 12 = 2
        assert chord.get_note_for_key(0, 2) == 2

    def test_major_scale(self):
        major = [0, 2, 4, 5, 7, 9, 11]
        chord = Chord([0, 2, 4], [0], 0, scale=major)
        # In C major: degree 0→C(0), degree 2→E(4), degree 4→G(7)
        assert chord.get_note_for_key(0, 0) == 0
        assert chord.get_note_for_key(2, 0) == 4
        assert chord.get_note_for_key(4, 0) == 7

    def test_major_scale_transposed(self):
        major = [0, 2, 4, 5, 7, 9, 11]
        chord = Chord([0, 2, 4], [0], 0, scale=major)
        # In D major (key=2): degree 0→D(2), degree 2→F#(6), degree 4→A(9)
        assert chord.get_note_for_key(0, 2) == 2
        assert chord.get_note_for_key(2, 2) == 6
        assert chord.get_note_for_key(4, 2) == 9

    def test_wrapping_around_scale_length(self):
        major = [0, 2, 4, 5, 7, 9, 11]
        chord = Chord([0, 2, 4], [0], 3, scale=major)
        # root=3 → note 0 maps to (0+3)%7=3 → scale[3]=5, +key=0 → 5 (F)
        assert chord.get_note_for_key(0, 0) == 5


class TestChordFindAllNotes:
    """Test Chord.find_all_notes — precomputes notes across all keys."""

    def test_returns_dict_with_12_keys(self):
        chord = Chord([0, 4, 7], [0], 0)
        notes, all_notes = chord.find_all_notes([0, 4, 7])
        assert len(notes) == 12
        assert len(all_notes) == 12

    def test_key_c_major_triad_note_classes(self):
        chord = Chord([0, 4, 7], [0], 0)
        notes, _ = chord.find_all_notes([0, 4, 7])
        assert notes[0] == [0, 4, 7]  # C, E, G

    def test_key_g_major_triad_note_classes(self):
        chord = Chord([0, 4, 7], [0], 0)
        notes, _ = chord.find_all_notes([0, 4, 7])
        # key=7 (G): (0+7)%12=7, (4+7)%12=11, (7+7)%12=2
        assert sorted(notes[7]) == [2, 7, 11]

    def test_all_notes_are_within_midi_range(self):
        chord = Chord([0, 4, 7], [0], 0)
        _, all_notes = chord.find_all_notes([0, 4, 7])
        for key in range(12):
            for note in all_notes[key]:
                assert 21 <= note <= 108


class TestChordGetChord:
    """Test full chord voicing via get_chord (uses state for inversion/spread/voice_count)."""

    def test_major_triad_in_c(self):
        chord = Chord([0, 4, 7], [0], 0)
        state_module.state.voice_count = 3
        state_module.state.key.value = 0
        result = chord.get_chord()
        assert len(result) == 3
        assert all(21 <= n <= 108 for n in result)
        assert result == sorted(result)
        assert sorted({n % 12 for n in result}) == [0, 4, 7]

    def test_key_transposition(self):
        chord = Chord([0, 4, 7], [0], 0)
        state_module.state.voice_count = 3
        state_module.state.key.value = 2  # D
        result = chord.get_chord()
        pitch_classes = sorted({n % 12 for n in result})
        assert pitch_classes == [2, 6, 9]  # D, F#, A

    def test_inversion_shifts_voicing(self):
        chord = Chord([0, 4, 7], [0], 0)
        state_module.state.voice_count = 3
        state_module.state.key.value = 0
        state_module.state.inversion.value = 0

        result_no_inv = chord.get_chord()

        state_module.state.inversion.value = 1
        result_inv1 = chord.get_chord()

        # With inversion, the bottom note index shifts — notes should differ
        assert result_no_inv != result_inv1

    def test_voice_count_affects_note_count(self):
        chord = Chord([0, 4, 7], [0], 0)
        state_module.state.key.value = 0
        state_module.state.voice_count = 3
        result3 = chord.get_chord()
        state_module.state.voice_count = 5
        result5 = chord.get_chord()
        assert len(result3) <= len(result5)


class TestChordGetBass:
    """Test bass note generation."""

    def test_bass_root_in_key_of_c(self):
        chord = Chord([0, 4, 7], [0], 0)
        state_module.state.key.value = 0
        bass = chord.get_bass()
        assert 21 <= bass <= 108
        assert bass % 12 == 0  # Root is C

    def test_bass_in_key_of_d(self):
        chord = Chord([0, 4, 7], [0], 0)
        state_module.state.key.value = 2
        bass = chord.get_bass()
        assert bass % 12 == 2  # Root is D

    def test_bass_position_shifts_note(self):
        chord = Chord([0, 4, 7], [0], 0)
        state_module.state.key.value = 0
        state_module.state.bass_position.value = 0
        bass0 = chord.get_bass()
        state_module.state.bass_position.value = 2
        bass2 = chord.get_bass()
        assert bass0 != bass2
