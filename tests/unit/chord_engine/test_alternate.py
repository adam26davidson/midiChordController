"""Tests for Alternate module — toggles between main and alternate voicing."""

from unittest.mock import MagicMock

import music_engine.chord_engine.chord_engine_state as state_module
from music_engine.chord_engine.internal_chord_engine.modules.alternate import Alternate


class TestAlternate:
    def test_set_true(self):
        mock_update = MagicMock()
        alt = Alternate(mock_update)
        state_module.state.alternate = False
        alt.set(True)
        assert state_module.state.alternate is True
        mock_update.assert_called_once()

    def test_set_false(self):
        mock_update = MagicMock()
        alt = Alternate(mock_update)
        state_module.state.alternate = True
        alt.set(False)
        assert state_module.state.alternate is False
        mock_update.assert_called_once()

    def test_set_same_value_no_update(self):
        mock_update = MagicMock()
        alt = Alternate(mock_update)
        state_module.state.alternate = True
        mock_update.reset_mock()
        alt.set(True)
        mock_update.assert_not_called()

    def test_parameters_key(self):
        alt = Alternate(MagicMock())
        params = alt._Alternate__get_parameters()  # type: ignore[unresolved-attribute]
        assert len(params) == 1
        assert params[0].key == "ALTERNATE"
