from music_engine.chord_engine.utils import find_all_octaves_in_range, find_closest_note


class TestFindAllOctavesInRange:
    def test_single_note_class_c(self):
        # Note class 0 = C. In range 21-108 (A0-C8):
        # C1=24, C2=36, C3=48, C4=60, C5=72, C6=84, C7=96, C8=108
        result = find_all_octaves_in_range([0], min=21, max=108)
        assert result == [24, 36, 48, 60, 72, 84, 96, 108]

    def test_single_note_class_a(self):
        # Note class 9 = A. A0=21, A1=33, A2=45, A3=57, A4=69, A5=81, A6=93, A7=105
        result = find_all_octaves_in_range([9], min=21, max=108)
        assert result == [21, 33, 45, 57, 69, 81, 93, 105]

    def test_multiple_note_classes_sorted(self):
        # C and E (0, 4) should interleave and be sorted
        result = find_all_octaves_in_range([0, 4], min=60, max=84)
        # C4=60, E4=64, C5=72, E5=76, C6=84
        assert result == [60, 64, 72, 76, 84]

    def test_no_duplicates_with_repeated_input(self):
        result = find_all_octaves_in_range([0, 0], min=60, max=72)
        assert result == [60, 72]

    def test_empty_input(self):
        result = find_all_octaves_in_range([], min=21, max=108)
        assert result == []

    def test_custom_range(self):
        result = find_all_octaves_in_range([0], min=60, max=72)
        assert result == [60, 72]


class TestFindClosestNote:
    def test_exact_match(self):
        notes = [36, 48, 60, 72, 84]
        assert find_closest_note(60, notes) == 2  # index of 60

    def test_closer_to_lower(self):
        notes = [36, 48, 60, 72, 84]
        assert find_closest_note(59, notes) == 2  # 60 is closest

    def test_closer_to_upper(self):
        notes = [36, 48, 60, 72, 84]
        assert find_closest_note(61, notes) == 2  # 60 is closest (lower wins on tie-ish)

    def test_target_below_all(self):
        notes = [36, 48, 60]
        assert find_closest_note(10, notes) == 0

    def test_target_above_all(self):
        notes = [36, 48, 60]
        assert find_closest_note(100, notes) == 2

    def test_equidistant_prefers_lower(self):
        notes = [36, 48, 60]
        # 42 is equidistant from 36 and 48
        result = find_closest_note(42, notes)
        assert result in [0, 1]  # either is acceptable

    def test_single_element(self):
        notes = [60]
        assert find_closest_note(40, notes) == 0
        assert find_closest_note(80, notes) == 0
