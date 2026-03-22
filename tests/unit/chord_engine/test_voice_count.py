from unittest.mock import MagicMock

import music_engine.chord_engine.chord_engine_state as state_module
from constants import MAX_VOICE_COUNT
from models.app_parameter import AppParameterType
from music_engine.chord_engine.modules.voice_count import VoiceCount


def make_voice_count(**kwargs):
    return VoiceCount(
        kwargs.get("type", AppParameterType.INTERNAL_CHORD_ENGINE),
        kwargs.get("update_chord_engine", MagicMock()),
    )


class TestVoiceCountSet:
    def test_set_basic(self):
        vc = make_voice_count()
        vc.set(5)
        assert state_module.state.voice_count == 5

    def test_set_clamps_max(self):
        vc = make_voice_count()
        vc.set(999)
        assert state_module.state.voice_count == MAX_VOICE_COUNT

    def test_set_clamps_to_minimum(self):
        vc = make_voice_count()
        vc.set(-5)
        assert state_module.state.voice_count == 1

    def test_set_calls_update(self):
        mock = MagicMock()
        vc = make_voice_count(update_chord_engine=mock)
        mock.reset_mock()
        vc.set(5)
        mock.assert_called_once()


class TestVoiceCountIncrementDecrement:
    def test_increment(self):
        vc = make_voice_count()
        state_module.state.voice_count = 4
        vc.increment()
        assert state_module.state.voice_count == 5

    def test_decrement(self):
        vc = make_voice_count()
        state_module.state.voice_count = 4
        vc.decrement()
        assert state_module.state.voice_count == 3

    def test_decrement_at_one(self):
        vc = make_voice_count()
        state_module.state.voice_count = 1
        vc.decrement()
        assert state_module.state.voice_count == 1

    def test_increment_at_max(self):
        vc = make_voice_count()
        state_module.state.voice_count = MAX_VOICE_COUNT
        vc.increment()
        assert state_module.state.voice_count == MAX_VOICE_COUNT
