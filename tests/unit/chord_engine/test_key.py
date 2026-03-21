from unittest.mock import MagicMock

import music_engine.chord_engine.chord_engine_state as state_module
from models.app_parameter import AppParameterType
from music_engine.chord_engine.modules.key import Key


def make_key(**kwargs):
    return Key(
        kwargs.get("type", AppParameterType.INTERNAL_CHORD_ENGINE),
        kwargs.get("update_chord_engine", MagicMock()),
    )


class TestKeySet:
    def test_set_basic(self):
        key = make_key()
        key.set(5)
        assert state_module.state.key.value == 5

    def test_set_wraps_at_12(self):
        key = make_key()
        key.set(14)
        assert state_module.state.key.value == 2

    def test_set_wraps_negative(self):
        key = make_key()
        key.set(24)
        assert state_module.state.key.value == 0

    def test_set_calls_update(self):
        mock = MagicMock()
        key = make_key(update_chord_engine=mock)
        mock.reset_mock()
        key.set(5)
        mock.assert_called_once()

    def test_set_noop_when_same(self):
        mock = MagicMock()
        key = make_key(update_chord_engine=mock)
        state_module.state.key.value = 5
        mock.reset_mock()
        key.set(5)
        mock.assert_not_called()


class TestKeyIncrement:
    def test_increment_by_default(self):
        key = make_key()
        state_module.state.key.value = 0
        state_module.state.key.increment_by = 1
        key.increment()
        assert state_module.state.key.value == 1

    def test_increment_wraps(self):
        key = make_key()
        state_module.state.key.value = 11
        state_module.state.key.increment_by = 1
        key.increment()
        assert state_module.state.key.value == 0

    def test_increment_by_semitones(self):
        key = make_key()
        state_module.state.key.value = 0
        state_module.state.key.increment_by = 5
        key.increment()
        assert state_module.state.key.value == 5

    def test_decrement_by_default(self):
        key = make_key()
        state_module.state.key.value = 3
        state_module.state.key.increment_by = 1
        key.decrement()
        assert state_module.state.key.value == 2

    def test_decrement_wraps(self):
        key = make_key()
        state_module.state.key.value = 0
        state_module.state.key.increment_by = 1
        key.decrement()
        assert state_module.state.key.value == 11

    def test_set_increment_by(self):
        key = make_key()
        key.set_increment_by(7)
        assert state_module.state.key.increment_by == 7


class TestKeyParameters:
    def test_internal_key_prefix(self):
        key = make_key(type=AppParameterType.INTERNAL_CHORD_ENGINE)
        params = key.get_parameters()
        assert len(params) == 1
        assert params[0].key == "INTERNAL_KEY"

    def test_external_key_prefix(self):
        key = make_key(type=AppParameterType.EXTERNAL_CHORD_ENGINE)
        params = key.get_parameters()
        assert params[0].key == "EXTERNAL_KEY"
