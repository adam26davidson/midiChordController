from unittest.mock import MagicMock

import music_engine.chord_engine.chord_engine_state as state_module
from models.app_parameter import AppParameterType
from music_engine.chord_engine.modules.hold import Hold


def make_hold(**kwargs):
    return Hold(
        kwargs.get("type", AppParameterType.INTERNAL_CHORD_ENGINE),
        kwargs.get("stop_chord_and_bass", MagicMock()),
    )


class TestHoldToggle:
    def test_toggle_on(self):
        hold = make_hold()
        state_module.state.hold = False
        hold.toggle()
        assert state_module.state.hold is True

    def test_toggle_off_calls_stop(self):
        mock_stop = MagicMock()
        hold = make_hold(stop_chord_and_bass=mock_stop)
        state_module.state.hold = True
        hold.toggle()
        assert state_module.state.hold is False
        mock_stop.assert_called_once()

    def test_toggle_on_does_not_call_stop(self):
        mock_stop = MagicMock()
        hold = make_hold(stop_chord_and_bass=mock_stop)
        state_module.state.hold = False
        hold.toggle()
        mock_stop.assert_not_called()

    def test_double_toggle_returns_to_original(self):
        hold = make_hold()
        state_module.state.hold = False
        hold.toggle()
        hold.toggle()
        assert state_module.state.hold is False


class TestHoldParameters:
    def test_internal_parameter_key(self):
        hold = make_hold(type=AppParameterType.INTERNAL_CHORD_ENGINE)
        # Access name-mangled method
        params = hold._Hold__get_parameters()
        assert params[0].key == "INTERNAL_HOLD"

    def test_external_parameter_key(self):
        hold = make_hold(type=AppParameterType.EXTERNAL_CHORD_ENGINE)
        params = hold._Hold__get_parameters()
        assert params[0].key == "EXTERNAL_HOLD"
