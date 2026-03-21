"""Tests for NoteHistory — tracking MIDI note input for external chord engine."""

import music_engine.chord_engine.chord_engine_state as state_module
from music_engine.chord_engine.external_chord_engine.modules.note_history import NoteHistory


def make_history():
    return NoteHistory()


class TestNoteOn:
    def test_first_note_sets_contiguous_classes(self):
        nh = make_history()
        nh.note_on(60)  # C4
        assert 0 in state_module.state.note_in_history.lastContiguousClasses

    def test_first_note_sets_lowest(self):
        nh = make_history()
        nh.note_on(60)
        assert state_module.state.note_in_history.lowest_in_contiguous_classes == 60

    def test_second_note_different_class_adds_to_contiguous(self):
        nh = make_history()
        nh.note_on(60)  # C
        nh.note_on(64)  # E
        assert 0 in state_module.state.note_in_history.lastContiguousClasses
        assert 4 in state_module.state.note_in_history.lastContiguousClasses

    def test_duplicate_class_not_added_twice(self):
        nh = make_history()
        nh.note_on(60)  # C4
        nh.note_on(72)  # C5 — same class
        classes = state_module.state.note_in_history.lastContiguousClasses
        assert classes.count(0) == 1

    def test_notes_played_tracked(self):
        nh = make_history()
        nh.note_on(60)
        nh.note_on(64)
        assert 60 in state_module.state.note_in_history.notesPlayed
        assert 64 in state_module.state.note_in_history.notesPlayed

    def test_classes_played_tracked(self):
        nh = make_history()
        nh.note_on(60)  # C
        nh.note_on(64)  # E
        assert 0 in state_module.state.note_in_history.classesPlayed
        assert 4 in state_module.state.note_in_history.classesPlayed

    def test_class_recency_ranking_most_recent_first(self):
        nh = make_history()
        nh.note_on(60)  # C
        nh.note_on(64)  # E
        nh.note_on(67)  # G
        ranking = state_module.state.note_in_history.classRecencyRanking
        assert ranking[0] == 7  # G most recent
        assert ranking[1] == 4  # E
        assert ranking[2] == 0  # C

    def test_replaying_note_moves_to_front_of_ranking(self):
        nh = make_history()
        nh.note_on(60)  # C
        nh.note_on(64)  # E
        nh.note_on(60)  # C again
        ranking = state_module.state.note_in_history.classRecencyRanking
        assert ranking[0] == 0  # C moved to front

    def test_lowest_updates_when_lower_note_played(self):
        nh = make_history()
        nh.note_on(64)  # E4
        nh.note_on(48)  # C3
        assert state_module.state.note_in_history.lowest_in_contiguous_classes == 48

    def test_lowest_does_not_update_when_higher_note_played(self):
        nh = make_history()
        nh.note_on(48)  # C3
        nh.note_on(64)  # E4
        assert state_module.state.note_in_history.lowest_in_contiguous_classes == 48


class TestNoteOff:
    def test_note_off_removes_from_notes_played(self):
        nh = make_history()
        nh.note_on(60)
        nh.note_off(60)
        assert 60 not in state_module.state.note_in_history.notesPlayed

    def test_note_off_removes_class_when_no_octaves_remain(self):
        nh = make_history()
        nh.note_on(60)  # C4
        nh.note_off(60)
        assert 0 not in state_module.state.note_in_history.classesPlayed

    def test_note_off_keeps_class_when_other_octave_remains(self):
        nh = make_history()
        nh.note_on(60)  # C4
        nh.note_on(72)  # C5
        nh.note_off(60)  # C4 off
        assert 0 in state_module.state.note_in_history.classesPlayed

    def test_note_off_nonexistent_does_not_crash(self):
        nh = make_history()
        nh.note_off(60)  # Never played — should not crash


class TestNoteHistory:
    def test_note_on_creates_history_event(self):
        nh = make_history()
        nh.note_on(60)
        history = state_module.state.note_in_history.all[0]
        assert len(history) >= 1
        assert history[-1].off_time is None  # Still on

    def test_note_off_sets_off_time(self):
        nh = make_history()
        nh.note_on(60)
        nh.note_off(60)
        history = state_module.state.note_in_history.all[0]
        assert history[-1].off_time is not None

    def test_chord_sequence(self):
        """Play C major triad, then release — verify full tracking."""
        nh = make_history()
        nh.note_on(60)  # C
        nh.note_on(64)  # E
        nh.note_on(67)  # G

        classes = sorted(state_module.state.note_in_history.lastContiguousClasses)
        assert classes == [0, 4, 7]
        assert len(state_module.state.note_in_history.notesPlayed) == 3

        nh.note_off(60)
        nh.note_off(64)
        nh.note_off(67)

        assert len(state_module.state.note_in_history.notesPlayed) == 0
        assert len(state_module.state.note_in_history.classesPlayed) == 0
