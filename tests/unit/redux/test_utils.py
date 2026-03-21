"""Tests for redux/utils.py — add_app_parameters and get_active_map."""


from models.app_parameter import AppParameter
from models.command import Command
from models.command_type import CommandType
from redux import store
from redux import utils as redux_utils


class TestAddAppParameters:
    def test_adds_parameters_to_empty_store(self):
        params = [
            AppParameter(
                valid_command_types=[CommandType.ON_OFF],
                command_mappings={Command.ON: lambda: None},
                key="TEST_1",
            ),
            AppParameter(
                valid_command_types=[CommandType.TOGGLE],
                command_mappings={Command.TOGGLE: lambda: None},
                key="TEST_2",
            ),
        ]
        redux_utils.add_app_parameters(params)

        state = store.get_state()["controllerCoupler"]
        assert "TEST_1" in state["appParameters"]
        assert "TEST_2" in state["appParameters"]

    def test_merges_with_existing_parameters(self):
        params1 = [
            AppParameter(
                valid_command_types=[CommandType.ON_OFF],
                command_mappings={Command.ON: lambda: None},
                key="FIRST",
            ),
        ]
        redux_utils.add_app_parameters(params1)

        params2 = [
            AppParameter(
                valid_command_types=[CommandType.TOGGLE],
                command_mappings={Command.TOGGLE: lambda: None},
                key="SECOND",
            ),
        ]
        redux_utils.add_app_parameters(params2)

        state = store.get_state()["controllerCoupler"]
        assert "FIRST" in state["appParameters"]
        assert "SECOND" in state["appParameters"]

    def test_overwrites_parameter_with_same_key(self):
        cb1 = lambda: "first"  # noqa: E731
        cb2 = lambda: "second"  # noqa: E731

        redux_utils.add_app_parameters([
            AppParameter(
                valid_command_types=[CommandType.ON_OFF],
                command_mappings={Command.ON: cb1},
                key="DUPE",
            ),
        ])
        redux_utils.add_app_parameters([
            AppParameter(
                valid_command_types=[CommandType.ON_OFF],
                command_mappings={Command.ON: cb2},
                key="DUPE",
            ),
        ])

        state = store.get_state()["controllerCoupler"]
        param = state["appParameters"]["DUPE"]
        assert param.command_mappings[Command.ON] is cb2


class TestGetActiveMap:
    def test_returns_none_with_no_controllers(self):
        result = redux_utils.get_active_me_map()
        assert result is None

    def test_returns_none_with_no_primary(self):
        # Add a non-primary controller
        action = {
            "type": "controllerManager/controllerAdded",
            "data": {
                "id": "ctrl1",
                "name": "Test",
                "role": "secondary",
                "compatibleMeMaps": [],
                "meMap": {"map": {"key": "value"}},
                "uiMap": {"map": {}},
            },
        }
        store.dispatch(action)
        result = redux_utils.get_active_me_map()
        assert result is None

    def test_returns_map_for_primary_controller(self):
        action = {
            "type": "controllerManager/controllerAdded",
            "data": {
                "id": "ctrl1",
                "name": "Test",
                "role": "primary",
                "compatibleMeMaps": [],
                "meMap": {"map": {"btn_south": ["CHORD_SOUTH"]}},
                "uiMap": {"map": {"btn_north": ["UI_ACTION"]}},
            },
        }
        store.dispatch(action)
        me_map = redux_utils.get_active_me_map()
        assert me_map == {"btn_south": ["CHORD_SOUTH"]}

        ui_map = redux_utils.get_active_ui_map()
        assert ui_map == {"btn_north": ["UI_ACTION"]}
