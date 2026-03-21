"""Tests for ChordEngine base class behavior via InternalChordEngine."""

from unittest.mock import MagicMock

import music_engine.chord_engine.chord_engine_state as state_module
from music_engine.chord_engine.chord_engine_message import ChordMessageType, ChordPlayer
from music_engine.chord_engine.internal_chord_engine import InternalChordEngine
from music_engine.chord_engine.state.chords_state import ChordButton


def make_engine():
    engine = InternalChordEngine()
    return engine


def make_engine_with_tracking():
    engine = make_engine()
    messages = []
    engine.callbacks = [lambda msg: messages.append(msg)]
    return engine, messages


class TestChordButtonQueue:
    def test_button_on_adds_to_queue(self):
        engine, _messages = make_engine_with_tracking()
        engine.chord_button_on(ChordButton.SOUTH)
        assert ChordButton.SOUTH in state_module.state.chord.button_queue

    def test_button_on_sends_chord_on(self):
        engine, messages = make_engine_with_tracking()
        engine.chord_button_on(ChordButton.SOUTH)
        on_messages = [m for m in messages if m.type == ChordMessageType.ON and m.player == ChordPlayer.CHORD]
        assert len(on_messages) >= 1

    def test_button_off_removes_from_queue(self):
        engine, _messages = make_engine_with_tracking()
        engine.chord_button_on(ChordButton.SOUTH)
        engine.chord_button_off(ChordButton.SOUTH)
        assert ChordButton.SOUTH not in state_module.state.chord.button_queue

    def test_button_off_sends_chord_off(self):
        engine, messages = make_engine_with_tracking()
        engine.chord_button_on(ChordButton.SOUTH)
        messages.clear()
        engine.chord_button_off(ChordButton.SOUTH)
        off_messages = [m for m in messages if m.type == ChordMessageType.OFF and m.player == ChordPlayer.CHORD]
        assert len(off_messages) >= 1

    def test_second_button_plays_new_chord(self):
        engine, messages = make_engine_with_tracking()
        engine.chord_button_on(ChordButton.SOUTH)
        messages.clear()
        engine.chord_button_on(ChordButton.WEST)
        # Should have sent OFF for south, ON for west
        on_messages = [m for m in messages if m.type == ChordMessageType.ON and m.player == ChordPlayer.CHORD]
        assert len(on_messages) >= 1

    def test_release_second_returns_to_first(self):
        engine, messages = make_engine_with_tracking()
        engine.chord_button_on(ChordButton.SOUTH)
        engine.chord_button_on(ChordButton.WEST)
        messages.clear()
        engine.chord_button_off(ChordButton.WEST)
        # Should replay south chord
        on_messages = [m for m in messages if m.type == ChordMessageType.ON and m.player == ChordPlayer.CHORD]
        assert len(on_messages) >= 1
        assert state_module.state.chord.button_queue[-1] == ChordButton.SOUTH

    def test_release_non_active_button_no_change(self):
        engine, messages = make_engine_with_tracking()
        engine.chord_button_on(ChordButton.SOUTH)
        engine.chord_button_on(ChordButton.WEST)
        messages.clear()
        engine.chord_button_off(ChordButton.SOUTH)
        # West is still active, no new chord messages
        on_messages = [m for m in messages if m.type == ChordMessageType.ON and m.player == ChordPlayer.CHORD]
        assert len(on_messages) == 0

    def test_duplicate_button_press_no_replay(self):
        engine, messages = make_engine_with_tracking()
        engine.chord_button_on(ChordButton.SOUTH)
        messages.clear()
        engine.chord_button_on(ChordButton.SOUTH)
        # Already active — should not send new ON
        on_messages = [m for m in messages if m.type == ChordMessageType.ON and m.player == ChordPlayer.CHORD]
        assert len(on_messages) == 0


class TestHoldBehavior:
    def test_hold_prevents_chord_off(self):
        engine, messages = make_engine_with_tracking()
        state_module.state.hold = True
        engine.chord_button_on(ChordButton.SOUTH)
        messages.clear()
        engine.chord_button_off(ChordButton.SOUTH)
        # Hold is on — chord should NOT stop
        off_messages = [m for m in messages if m.type == ChordMessageType.OFF and m.player == ChordPlayer.CHORD]
        assert len(off_messages) == 0

    def test_stop_chord_and_bass_forces_stop(self):
        engine, messages = make_engine_with_tracking()
        engine.chord_button_on(ChordButton.SOUTH)
        engine.play_bass()  # Explicitly start bass
        messages.clear()
        engine.stop_chord_and_bass()
        chord_off = [m for m in messages if m.type == ChordMessageType.OFF and m.player == ChordPlayer.CHORD]
        bass_off = [m for m in messages if m.type == ChordMessageType.OFF and m.player == ChordPlayer.BASS]
        assert len(chord_off) >= 1
        assert len(bass_off) >= 1


class TestBassPlayback:
    def test_play_bass_sends_on(self):
        engine, messages = make_engine_with_tracking()
        engine.chord_button_on(ChordButton.SOUTH)
        messages.clear()
        engine.play_bass()  # Bass must be explicitly triggered
        bass_on = [m for m in messages if m.type == ChordMessageType.ON and m.player == ChordPlayer.BASS]
        assert len(bass_on) >= 1

    def test_bass_note_is_single(self):
        engine, messages = make_engine_with_tracking()
        engine.chord_button_on(ChordButton.SOUTH)
        messages.clear()
        engine.play_bass()
        bass_on = [m for m in messages if m.type == ChordMessageType.ON and m.player == ChordPlayer.BASS]
        assert len(bass_on[0].notes) == 1


class TestSubscribe:
    def test_subscribe_adds_callback(self):
        engine = make_engine()
        cb = MagicMock()
        engine.subscribe(cb)
        assert cb in engine.callbacks

    def test_multiple_subscribers(self):
        engine = make_engine()
        cb1 = MagicMock()
        cb2 = MagicMock()
        engine.subscribe(cb1)
        engine.subscribe(cb2)
        engine.chord_button_on(ChordButton.SOUTH)
        cb1.assert_called()
        cb2.assert_called()
