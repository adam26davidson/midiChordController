"""Tests for Midi output path — note on/off byte construction, handle_message routing."""


from music_engine.midi import Midi


class TestHandleMessage:
    def test_note_on_message(self):
        midi = Midi()
        midi.state["velocityMode"] = "constant"
        midi.state["velocity"] = 100
        sent = []
        midi.midi_out_instances = [type("MockOut", (), {"send_message": lambda self, msg: sent.append(msg)})()]

        midi.handle_message({"note": 60, "type": "on", "player": "chord"})
        # First message is NOTE_ON, subsequent may be aftertouch
        note_on = sent[0]
        assert note_on[0] & 0xF0 == 0x90
        assert note_on[1] == 60
        assert note_on[2] == 100

    def test_note_off_message(self):
        midi = Midi()
        midi.state["velocityMode"] = "constant"
        midi.state["velocity"] = 100
        sent = []
        midi.midi_out_instances = [type("MockOut", (), {"send_message": lambda self, msg: sent.append(msg)})()]

        # Must turn on first so there's state to turn off
        midi.handle_message({"note": 60, "type": "on", "player": "chord"})
        sent.clear()
        midi.handle_message({"note": 60, "type": "off", "player": "chord"})
        assert len(sent) == 1
        # NOTE_OFF is 0x80, channel 0 → 0x80
        assert sent[0][0] & 0xF0 == 0x80
        assert sent[0][1] == 60
        assert sent[0][2] == 0

    def test_bass_uses_bass_channel(self):
        midi = Midi()
        midi.state["velocityMode"] = "constant"
        midi.state["velocity"] = 100
        midi.state["bassChannel"] = 3
        sent = []
        midi.midi_out_instances = [type("MockOut", (), {"send_message": lambda self, msg: sent.append(msg)})()]

        midi.handle_message({"note": 36, "type": "on", "player": "bass"})
        assert sent[0][0] & 0x0F == 3  # Channel 3

    def test_chord_uses_chord_channel(self):
        midi = Midi()
        midi.state["velocityMode"] = "constant"
        midi.state["velocity"] = 100
        midi.state["chordChannel"] = 5
        sent = []
        midi.midi_out_instances = [type("MockOut", (), {"send_message": lambda self, msg: sent.append(msg)})()]

        midi.handle_message({"note": 60, "type": "on", "player": "chord"})
        assert sent[0][0] & 0x0F == 5  # Channel 5

    def test_multiple_notes_sent_to_outputs(self):
        midi = Midi()
        midi.state["velocityMode"] = "constant"
        midi.state["velocity"] = 100
        sent1 = []
        sent2 = []
        midi.midi_out_instances = [
            type("MockOut", (), {"send_message": lambda self, msg, s=sent1: s.append(msg)})(),
            type("MockOut", (), {"send_message": lambda self, msg, s=sent2: s.append(msg)})(),
        ]
        midi.handle_message({"note": 60, "type": "on", "player": "chord"})
        # Both outputs receive the same messages (NOTE_ON + aftertouch)
        assert len(sent1) >= 1
        assert len(sent2) >= 1
        assert sent1[0] == sent2[0]  # Same NOTE_ON message


class TestCombineCommandAndChannel:
    def test_note_on_channel_0(self):
        midi = Midi()
        result = midi._Midi__combine_command_and_channel(0x90, 0)
        assert result == 0x90

    def test_note_on_channel_5(self):
        midi = Midi()
        result = midi._Midi__combine_command_and_channel(0x90, 5)
        assert result == 0x95

    def test_note_off_channel_15(self):
        midi = Midi()
        result = midi._Midi__combine_command_and_channel(0x80, 15)
        assert result == 0x8F

    def test_channel_masked_to_4_bits(self):
        midi = Midi()
        # Channel > 15 should be masked
        result = midi._Midi__combine_command_and_channel(0x90, 0x1F)
        assert result == 0x9F  # Only lower nibble


class TestHandleMidiIn:
    def test_note_on_parsed(self):
        midi = Midi()
        messages = []
        midi.subscriber_callbacks.append(lambda msg: messages.append(msg))

        # NOTE_ON (0x90) on channel 0, note 60, velocity 100
        midi.handle_midi_in(([0x90, 60, 100],), "test_port")
        assert len(messages) == 1
        assert messages[0].note == 60

    def test_note_off_parsed(self):
        midi = Midi()
        messages = []
        midi.subscriber_callbacks.append(lambda msg: messages.append(msg))

        # First note on
        midi.handle_midi_in(([0x90, 60, 100],), "test_port")
        # Then note off (0x80)
        midi.handle_midi_in(([0x80, 60, 0],), "test_port")
        assert len(messages) == 2

    def test_note_on_velocity_zero_is_note_off(self):
        midi = Midi()
        messages = []
        midi.subscriber_callbacks.append(lambda msg: messages.append(msg))

        midi.handle_midi_in(([0x90, 60, 100],), "test_port")
        # NOTE_ON with velocity 0 = NOTE_OFF
        midi.handle_midi_in(([0x90, 60, 0],), "test_port")
        assert len(messages) == 2

    def test_different_channels_parsed(self):
        midi = Midi()
        messages = []
        midi.subscriber_callbacks.append(lambda msg: messages.append(msg))

        # NOTE_ON on channel 5
        midi.handle_midi_in(([0x95, 60, 100],), "port_a")
        assert len(messages) == 1
        assert messages[0].note == 60


class TestDistributeChannels:
    def test_notes_get_different_channels(self):
        midi = Midi()
        midi.state["distributeChannels"] = True
        midi.state["velocityMode"] = "constant"
        midi.state["velocity"] = 100
        sent = []
        midi.midi_out_instances = [type("MockOut", (), {"send_message": lambda self, msg: sent.append(list(msg))})()]

        midi.handle_message({"note": 60, "type": "on", "player": "chord"})
        midi.handle_message({"note": 64, "type": "on", "player": "chord"})

        ch1 = sent[0][0] & 0x0F
        ch2 = sent[1][0] & 0x0F
        assert ch1 != ch2

    def test_note_off_uses_same_channel_as_on(self):
        midi = Midi()
        midi.state["distributeChannels"] = True
        midi.state["velocityMode"] = "constant"
        midi.state["velocity"] = 100
        sent = []
        midi.midi_out_instances = [type("MockOut", (), {"send_message": lambda self, msg: sent.append(list(msg))})()]

        midi.handle_message({"note": 60, "type": "on", "player": "chord"})
        on_channel = midi.state["distChordChannels"][60]
        midi.handle_message({"note": 60, "type": "off", "player": "chord"})
        # After note-off, the channel record should still reflect what was used
        assert midi.state["distChordChannels"][60] == on_channel
