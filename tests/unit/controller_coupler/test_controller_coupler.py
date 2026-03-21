"""Tests for ControllerCoupler event routing and parameter mapping."""

from unittest.mock import MagicMock

from controller_coupler import ChordEngineControlMode, ControllerCoupler
from controller_manager.models.control_event import ControlEvent
from controller_manager.models.mappable_control_event import MappableControlEvent
from models.app_parameter import AppParameter, AppParameterType
from models.command import Command
from models.command_type import CommandType


def make_coupler_with_param(key="TEST_PARAM", control_key="btn_south", **param_kwargs):
    """Create a ControllerCoupler with a single parameter mapped to a control key."""
    coupler = ControllerCoupler()
    callback = param_kwargs.pop("callback", MagicMock())
    param = AppParameter(
        valid_command_types=param_kwargs.get("valid_command_types", [CommandType.ON_OFF]),
        command_mappings=param_kwargs.get("command_mappings", {
            Command.ON: callback,
            Command.OFF: MagicMock(),
        }),
        key=key,
        type=param_kwargs.get("type", AppParameterType.MUSIC_ENGINE),
    )
    coupler.parameters = {key: param}
    coupler.map.map[control_key] = [key]
    return coupler, callback


class TestEventRouting:
    def test_on_event_calls_on_command(self):
        coupler, callback = make_coupler_with_param()
        event = ControlEvent(
            control_key="btn_south",
            event=MappableControlEvent.ON,
            controller_id="test",
            value=None,
        )
        coupler.event_handler(event)
        callback.assert_called_once()

    def test_off_event_calls_off_command(self):
        off_callback = MagicMock()
        coupler, _ = make_coupler_with_param(
            command_mappings={
                Command.ON: MagicMock(),
                Command.OFF: off_callback,
            }
        )
        event = ControlEvent(
            control_key="btn_south",
            event=MappableControlEvent.OFF,
            controller_id="test",
            value=None,
        )
        coupler.event_handler(event)
        off_callback.assert_called_once()

    def test_update_event_passes_value(self):
        update_callback = MagicMock()
        coupler, _ = make_coupler_with_param(
            valid_command_types=[CommandType.ANALOG],
            command_mappings={Command.UPDATE: update_callback},
        )
        event = ControlEvent(
            control_key="btn_south",
            event=MappableControlEvent.UPDATE,
            controller_id="test",
            value=0.75,
        )
        coupler.event_handler(event)
        update_callback.assert_called_once_with(0.75)

    def test_unknown_control_key_silently_ignored(self):
        coupler, callback = make_coupler_with_param()
        event = ControlEvent(
            control_key="nonexistent_key",
            event=MappableControlEvent.ON,
            controller_id="test",
            value=None,
        )
        coupler.event_handler(event)
        callback.assert_not_called()

    def test_positive_event_maps_to_increment(self):
        inc_callback = MagicMock()
        coupler, _ = make_coupler_with_param(
            valid_command_types=[CommandType.INCREMENTAL],
            command_mappings={
                Command.INCREMENT: inc_callback,
                Command.DECREMENT: MagicMock(),
            },
        )
        event = ControlEvent(
            control_key="btn_south",
            event=MappableControlEvent.POSITIVE,
            controller_id="test",
            value=None,
        )
        coupler.event_handler(event)
        inc_callback.assert_called_once()

    def test_negative_event_maps_to_decrement(self):
        dec_callback = MagicMock()
        coupler, _ = make_coupler_with_param(
            valid_command_types=[CommandType.INCREMENTAL],
            command_mappings={
                Command.INCREMENT: MagicMock(),
                Command.DECREMENT: dec_callback,
            },
        )
        event = ControlEvent(
            control_key="btn_south",
            event=MappableControlEvent.NEGATIVE,
            controller_id="test",
            value=None,
        )
        coupler.event_handler(event)
        dec_callback.assert_called_once()

    def test_toggle_parameter_uses_toggle_command(self):
        toggle_callback = MagicMock()
        coupler, _ = make_coupler_with_param(
            valid_command_types=[CommandType.TOGGLE],
            command_mappings={Command.TOGGLE: toggle_callback},
        )
        event = ControlEvent(
            control_key="btn_south",
            event=MappableControlEvent.ON,
            controller_id="test",
            value=None,
        )
        coupler.event_handler(event)
        toggle_callback.assert_called_once()


class TestChordEngineControlMode:
    def test_internal_param_blocked_in_external_mode(self):
        coupler, callback = make_coupler_with_param(
            type=AppParameterType.INTERNAL_CHORD_ENGINE,
        )
        coupler.chord_engine_control_mode = ChordEngineControlMode.EXTERNAL
        event = ControlEvent(
            control_key="btn_south",
            event=MappableControlEvent.ON,
            controller_id="test",
            value=None,
        )
        coupler.event_handler(event)
        callback.assert_not_called()

    def test_external_param_blocked_in_internal_mode(self):
        coupler, callback = make_coupler_with_param(
            type=AppParameterType.EXTERNAL_CHORD_ENGINE,
        )
        coupler.chord_engine_control_mode = ChordEngineControlMode.INTERNAL
        event = ControlEvent(
            control_key="btn_south",
            event=MappableControlEvent.ON,
            controller_id="test",
            value=None,
        )
        coupler.event_handler(event)
        callback.assert_not_called()

    def test_music_engine_param_not_blocked(self):
        coupler, callback = make_coupler_with_param(
            type=AppParameterType.MUSIC_ENGINE,
        )
        coupler.chord_engine_control_mode = ChordEngineControlMode.EXTERNAL
        event = ControlEvent(
            control_key="btn_south",
            event=MappableControlEvent.ON,
            controller_id="test",
            value=None,
        )
        coupler.event_handler(event)
        callback.assert_called_once()

    def test_internal_param_allowed_in_internal_mode(self):
        coupler, callback = make_coupler_with_param(
            type=AppParameterType.INTERNAL_CHORD_ENGINE,
        )
        coupler.chord_engine_control_mode = ChordEngineControlMode.INTERNAL
        event = ControlEvent(
            control_key="btn_south",
            event=MappableControlEvent.ON,
            controller_id="test",
            value=None,
        )
        coupler.event_handler(event)
        callback.assert_called_once()


class TestProcessNewParameters:
    def test_creates_increment_decrement_wrappers(self):
        coupler = ControllerCoupler()
        inc = MagicMock()
        dec = MagicMock()
        params = {
            "TEST": AppParameter(
                valid_command_types=[CommandType.INCREMENTAL],
                command_mappings={Command.INCREMENT: inc, Command.DECREMENT: dec},
                key="TEST",
            )
        }
        new_params = coupler.process_new_parameters(params)
        keys = [p.key for p in new_params]
        assert "INCREMENT_TEST" in keys
        assert "DECREMENT_TEST" in keys

    def test_no_wrappers_for_on_off_only(self):
        coupler = ControllerCoupler()
        params = {
            "TEST": AppParameter(
                valid_command_types=[CommandType.ON_OFF],
                command_mappings={Command.ON: MagicMock(), Command.OFF: MagicMock()},
                key="TEST",
            )
        }
        new_params = coupler.process_new_parameters(params)
        assert len(new_params) == 0

    def test_wrapper_on_calls_increment(self):
        coupler = ControllerCoupler()
        inc = MagicMock()
        params = {
            "TEST": AppParameter(
                valid_command_types=[CommandType.INCREMENTAL],
                command_mappings={Command.INCREMENT: inc, Command.DECREMENT: MagicMock()},
                key="TEST",
            )
        }
        new_params = coupler.process_new_parameters(params)
        inc_param = next(p for p in new_params if p.key == "INCREMENT_TEST")
        inc_param.command_mappings[Command.ON]()
        inc.assert_called_once()
