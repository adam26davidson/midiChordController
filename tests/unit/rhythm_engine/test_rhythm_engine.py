"""Tests for RhythmEngine interval generation and message routing."""


import numpy as np

from music_engine.chord_engine.chord_engine_message import ChordEngineMessage, ChordMessageType, ChordPlayer
from music_engine.rhythm_engine import RhythmEngine, ScheduledNotes


class TestScheduledNotes:
    def test_initial_generation_is_zero(self):
        sn = ScheduledNotes()
        assert sn.generation == 0

    def test_cancel_all_increments_generation(self):
        sn = ScheduledNotes()
        sn.cancel_all()
        assert sn.generation == 1
        sn.cancel_all()
        assert sn.generation == 2


class TestRhythmEngineIntervals:
    def _make_engine(self):
        engine = RhythmEngine()
        engine.state["strumInterval"] = 0.02
        return engine

    def test_regular_intervals_single_note(self):
        engine = self._make_engine()
        engine.state["strumMode"] = "regular"
        result = engine._RhythmEngine__get_regular_intervals(1)
        assert result == [0.0]

    def test_regular_intervals_four_notes(self):
        engine = self._make_engine()
        engine.state["strumMode"] = "regular"
        result = engine._RhythmEngine__get_regular_intervals(4)
        assert len(result) == 4
        assert result[0] == 0.0
        assert abs(result[1] - 0.02) < 1e-10
        assert abs(result[2] - 0.04) < 1e-10
        assert abs(result[3] - 0.06) < 1e-10

    def test_random_intervals_length(self):
        engine = self._make_engine()
        np.random.seed(42)
        result = engine._RhythmEngine__get_random_intervals(4)
        assert len(result) == 4
        assert all(v >= 0 for v in result)

    def test_off_mode_returns_zeros(self):
        engine = self._make_engine()
        engine.state["strumMode"] = "off"
        result = engine._RhythmEngine__get_intervals(4)
        assert result == [0, 0, 0, 0]

    def test_regular_mode_ascending(self):
        engine = self._make_engine()
        engine.state["strumMode"] = "regular"
        engine.state["strumOrder"] = "up"
        result = engine._RhythmEngine__get_intervals(4)
        assert len(result) == 4
        # Should be non-decreasing (ascending strum order)
        assert all(result[i] <= result[i + 1] for i in range(len(result) - 1))


class TestRhythmEngineMessageRouting:
    def _make_engine_with_callback(self):
        engine = RhythmEngine()
        engine.state["strumMode"] = "off"
        messages = []
        engine.subscribe(lambda msg: messages.append(msg))
        return engine, messages

    def test_chord_off_sends_all_notes(self):
        engine, messages = self._make_engine_with_callback()
        msg = ChordEngineMessage(
            type=ChordMessageType.OFF,
            notes=[60, 64, 67],
            player=ChordPlayer.CHORD,
        )
        engine.handle_message(msg)
        assert len(messages) == 3
        assert all(m["type"] == "off" for m in messages)
        assert all(m["player"] == "chord" for m in messages)

    def test_chord_on_strum_off_sends_immediately(self):
        engine, messages = self._make_engine_with_callback()
        msg = ChordEngineMessage(
            type=ChordMessageType.ON,
            notes=[60, 64, 67],
            player=ChordPlayer.CHORD,
        )
        engine.handle_message(msg)
        assert len(messages) == 3
        assert all(m["type"] == "on" for m in messages)

    def test_bass_on(self):
        engine, messages = self._make_engine_with_callback()
        msg = ChordEngineMessage(
            type=ChordMessageType.ON,
            notes=[36],
            player=ChordPlayer.BASS,
        )
        engine.handle_message(msg)
        assert len(messages) == 1
        assert messages[0]["note"] == 36
        assert messages[0]["type"] == "on"
        assert messages[0]["player"] == "bass"

    def test_bass_off(self):
        engine, messages = self._make_engine_with_callback()
        msg = ChordEngineMessage(
            type=ChordMessageType.OFF,
            notes=[36],
            player=ChordPlayer.BASS,
        )
        engine.handle_message(msg)
        assert len(messages) == 1
        assert messages[0]["type"] == "off"
        assert messages[0]["player"] == "bass"

    def test_chord_off_cancels_scheduled(self):
        engine, _messages = self._make_engine_with_callback()
        # Ensure cancel_all is called on chord off
        gen_before = engine.scheduled_notes.generation
        msg = ChordEngineMessage(
            type=ChordMessageType.OFF,
            notes=[60],
            player=ChordPlayer.CHORD,
        )
        engine.handle_message(msg)
        assert engine.scheduled_notes.generation == gen_before + 1
