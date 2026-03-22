"""Tests for Midi class state management (not actual MIDI I/O)."""

import math

from music_engine.midi import Midi


class TestMidiStateInit:
    def test_initial_state(self):
        midi = Midi()
        assert midi.state["velocity"] == 100
        assert midi.state["velocityMode"] == "random"
        assert midi.state["distributeChannels"] is False
        assert midi.state["chordChannel"] == 0
        assert midi.state["bassChannel"] == 0
        assert midi.state["aftertouchMode"] == "channel"

    def test_initial_playing_state_empty(self):
        midi = Midi()
        assert midi.state["playingChordNotes"] == []
        assert midi.state["playingBassNote"] is None
        # occupiedChannels is initialized for all 16 channels
        assert len(midi.state["occupiedChannels"]) == 16


class TestMidiNoteTracking:
    def test_store_chord_note_on(self):
        midi = Midi()
        midi._Midi__store_note_on(60, "chord")  # type: ignore[unresolved-attribute]
        assert 60 in midi.state["playingChordNotes"]

    def test_store_chord_note_off(self):
        midi = Midi()
        midi._Midi__store_note_on(60, "chord")  # type: ignore[unresolved-attribute]
        midi._Midi__store_note_off(60, "chord")  # type: ignore[unresolved-attribute]
        assert 60 not in midi.state["playingChordNotes"]

    def test_store_bass_note_on(self):
        midi = Midi()
        midi._Midi__store_note_on(36, "bass")  # type: ignore[unresolved-attribute]
        assert midi.state["playingBassNote"] == 36

    def test_store_bass_note_off(self):
        midi = Midi()
        midi._Midi__store_note_on(36, "bass")  # type: ignore[unresolved-attribute]
        midi._Midi__store_note_off(36, "bass")  # type: ignore[unresolved-attribute]
        assert midi.state["playingBassNote"] is None

    def test_multiple_chord_notes(self):
        midi = Midi()
        midi._Midi__store_note_on(60, "chord")  # type: ignore[unresolved-attribute]
        midi._Midi__store_note_on(64, "chord")  # type: ignore[unresolved-attribute]
        midi._Midi__store_note_on(67, "chord")  # type: ignore[unresolved-attribute]
        assert midi.state["playingChordNotes"] == [60, 64, 67]

    def test_duplicate_chord_note_not_added(self):
        midi = Midi()
        midi._Midi__store_note_on(60, "chord")  # type: ignore[unresolved-attribute]
        midi._Midi__store_note_on(60, "chord")  # type: ignore[unresolved-attribute]
        assert midi.state["playingChordNotes"].count(60) == 1

    def test_duplicate_chord_note_does_not_set_bass(self):
        """Regression: duplicate chord note previously fell through to set bass."""
        midi = Midi()
        midi._Midi__store_note_on(60, "chord")  # type: ignore[unresolved-attribute]
        midi._Midi__store_note_on(60, "chord")  # type: ignore[unresolved-attribute]  # Duplicate
        assert midi.state["playingBassNote"] is None


class TestMidiChannelDistribution:
    def test_distribute_channel_assigns_first_free(self):
        midi = Midi()
        midi.state["distributeChannels"] = True
        # Channel 0 is occupied by bass by default
        ch = midi._Midi__distribute_channel()  # type: ignore[unresolved-attribute]
        assert midi.state["occupiedChannels"][ch] is True

    def test_distribute_channel_sequential(self):
        midi = Midi()
        midi.state["distributeChannels"] = True
        ch1 = midi._Midi__distribute_channel()  # type: ignore[unresolved-attribute]
        ch2 = midi._Midi__distribute_channel()  # type: ignore[unresolved-attribute]
        assert ch1 != ch2

    def test_open_channel_frees_it(self):
        midi = Midi()
        midi.state["distributeChannels"] = True
        ch = midi._Midi__distribute_channel()  # type: ignore[unresolved-attribute]
        midi.state["distChordChannels"][60] = ch
        midi._Midi__open_channel(60, "chord")  # type: ignore[unresolved-attribute]
        assert midi.state["occupiedChannels"][ch] is False


class TestMidiVelocity:
    def test_constant_velocity(self):
        midi = Midi()
        midi.state["velocity"] = 100
        midi.state["velocityMode"] = "constant"
        vel = midi._Midi__get_velocity()  # type: ignore[unresolved-attribute]
        assert vel == 100

    def test_random_velocity_within_range(self):
        midi = Midi()
        midi.state["velocity"] = 100
        midi.state["velocityMode"] = "random"
        midi.state["velocityDeviation"] = 10
        for _ in range(20):
            vel = midi._Midi__get_velocity()  # type: ignore[unresolved-attribute]
            assert 0 <= vel <= 127


class TestMidiAftertouch:
    def test_set_after_touch_converts_range(self):
        midi = Midi()
        # Formula: math.floor(((value+1) / 2) * 128)
        midi.set_after_touch(-1.0)
        assert midi.state["afterTouch"] == math.floor(((- 1.0 + 1) / 2) * 128)  # 0

        midi.set_after_touch(0.0)
        assert midi.state["afterTouch"] == math.floor(((0.0 + 1) / 2) * 128)  # 64

        midi.set_after_touch(0.5)
        assert midi.state["afterTouch"] == math.floor(((0.5 + 1) / 2) * 128)  # 96


class TestMidiAftertouchClamp:
    def test_aftertouch_clamped_to_127(self):
        """Regression: value=1.0 previously produced 128 (out of MIDI range)."""
        midi = Midi()
        midi.set_after_touch(1.0)
        assert midi.state["afterTouch"] <= 127

    def test_cc_clamped_to_127(self):
        """Regression: value=1.0 previously produced 128 (out of MIDI range)."""
        midi = Midi()
        setter = midi.get_cc_setter(1)
        setter(1.0)
        assert midi.state["CCValues"][1] <= 127


class TestMidiCCSetter:
    def test_cc_setter_closure(self):
        midi = Midi()
        setter = midi.get_cc_setter(1)
        setter(0.5)
        expected = math.floor(((0.5 + 1) / 2) * 128)
        assert midi.state["CCValues"][1] == expected

    def test_cc_setter_min(self):
        midi = Midi()
        setter = midi.get_cc_setter(7)
        setter(-1.0)
        assert midi.state["CCValues"][7] == 0

    def test_cc_setter_max(self):
        midi = Midi()
        setter = midi.get_cc_setter(7)
        setter(1.0)
        assert midi.state["CCValues"][7] == 127  # Clamped to valid MIDI range


class TestMidiInputNoteTracking:
    def test_add_midi_input_note_on(self):
        midi = Midi()
        messages = []
        midi.subscriber_callbacks.append(lambda msg: messages.append(msg))
        midi.add_midi_input_note_on(60, 0, "controller1")
        assert 60 in midi.state["midiInputNotesOn"]
        assert 60 in midi.state["mergedMidiInputNotesOn"]
        assert len(messages) == 1

    def test_duplicate_note_same_source_no_message(self):
        midi = Midi()
        messages = []
        midi.subscriber_callbacks.append(lambda msg: messages.append(msg))
        midi.add_midi_input_note_on(60, 0, "ctrl1")
        midi.add_midi_input_note_on(60, 0, "ctrl1")
        assert len(messages) == 1  # Only first sends message

    def test_remove_midi_input_note_off(self):
        midi = Midi()
        messages = []
        midi.subscriber_callbacks.append(lambda msg: messages.append(msg))
        midi.add_midi_input_note_on(60, 0, "ctrl1")
        midi.remove_midi_input_note_on(60, 0, "ctrl1")
        assert 60 not in midi.state["mergedMidiInputNotesOn"]
        assert len(messages) == 2  # ON + OFF
