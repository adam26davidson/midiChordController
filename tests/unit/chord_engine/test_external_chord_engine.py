"""Tests for ExternalChordEngine pure logic methods (chord recognition, rotation, scale matching)."""

from music_engine.chord_engine.external_chord_engine import ExternalChordEngine


def make_engine():
    return ExternalChordEngine()


class TestRotateBack:
    def test_rotate_back_by_zero(self):
        engine = make_engine()
        assert engine.rotate_back(0, [0, 4, 7]) == [0, 4, 7]

    def test_rotate_back_by_two(self):
        engine = make_engine()
        # [0, 4, 7] rotated back by 2 → [(0+10)%12, (4+10)%12, (7+10)%12] = [10, 2, 5]
        assert engine.rotate_back(2, [0, 4, 7]) == [2, 5, 10]

    def test_rotate_back_by_seven(self):
        engine = make_engine()
        # [0, 4, 7] → [(0+5)%12, (4+5)%12, (7+5)%12] = [5, 9, 0]
        assert engine.rotate_back(7, [0, 4, 7]) == [0, 5, 9]


class TestRotateForward:
    def test_rotate_forward_by_zero(self):
        engine = make_engine()
        assert engine.rotate_forward(0, [0, 4, 7]) == [0, 4, 7]

    def test_rotate_forward_by_two(self):
        engine = make_engine()
        assert engine.rotate_forward(2, [0, 4, 7]) == [2, 6, 9]

    def test_rotate_forward_by_seven(self):
        engine = make_engine()
        # [0, 4, 7] → [7, 11, 2]
        assert engine.rotate_forward(7, [0, 4, 7]) == [2, 7, 11]

    def test_rotate_forward_wraps(self):
        engine = make_engine()
        assert engine.rotate_forward(11, [0, 4, 7]) == [3, 6, 11]


class TestNotesFitInScale:
    def test_notes_fit_in_chromatic(self):
        engine = make_engine()
        chromatic = list(range(12))
        assert engine.notes_fit_in_scale([0, 4, 7], chromatic) is True

    def test_notes_fit_in_major_scale(self):
        engine = make_engine()
        c_major = [0, 2, 4, 5, 7, 9, 11]
        assert engine.notes_fit_in_scale([0, 4, 7], c_major) is True  # C major triad

    def test_notes_dont_fit(self):
        engine = make_engine()
        c_major = [0, 2, 4, 5, 7, 9, 11]
        assert engine.notes_fit_in_scale([0, 1, 7], c_major) is False  # Db not in C major

    def test_empty_notes_fit(self):
        engine = make_engine()
        assert engine.notes_fit_in_scale([], [0, 2, 4]) is True


class TestGetPrimeForm:
    def test_major_triad(self):
        engine = make_engine()
        result = engine.get_prime_form([0, 4, 7])
        assert result == [0, 4, 7]

    def test_major_triad_first_inversion(self):
        engine = make_engine()
        # [4, 7, 0] → rotating back by 7 gives [0, 5, 9] (sum=14)
        # rotating back by 0 gives [0, 4, 7] (sum=11) — lowest
        result = engine.get_prime_form([4, 7, 0])
        assert result == [0, 4, 7]

    def test_minor_triad(self):
        engine = make_engine()
        result = engine.get_prime_form([0, 3, 7])
        assert result == [0, 3, 7]

    def test_transposed_major_triad(self):
        engine = make_engine()
        # D major: [2, 6, 9]
        result = engine.get_prime_form([2, 6, 9])
        # Rotating back by 2 gives [0, 4, 7] (sum=11)
        assert result == [0, 4, 7]


class TestUseNotesAsScale:
    def test_basic(self):
        engine = make_engine()
        key, scale = engine.use_notes_as_scale([2, 6, 9])
        assert key == 2
        # Scale should be notes rotated back by key (2)
        assert scale == [0, 4, 7]

    def test_empty(self):
        engine = make_engine()
        key, scale = engine.use_notes_as_scale([])
        assert key == 0
        assert scale == []

    def test_single_note(self):
        engine = make_engine()
        key, scale = engine.use_notes_as_scale([5])
        assert key == 5
        assert scale == [0]
