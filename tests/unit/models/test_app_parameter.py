from models.app_parameter import AppParameter, AppParameterType
from models.command import Command
from models.command_type import CommandType


class TestAppParameter:
    def test_construction_with_defaults(self):
        param = AppParameter(
            valid_command_types=[CommandType.ON_OFF],
            command_mappings={Command.ON: lambda: None},
            key="TEST",
        )
        assert param.key == "TEST"
        assert param.remappable is True
        assert param.type == AppParameterType.MUSIC_ENGINE
        assert param.label is None
        assert param.label_abreviation is None

    def test_construction_with_all_fields(self):
        callback = lambda: None  # noqa: E731
        param = AppParameter(
            valid_command_types=[CommandType.TOGGLE],
            command_mappings={Command.TOGGLE: callback},
            key="MY_PARAM",
            label="My Param",
            label_abreviation="MP",
            remappable=False,
            type=AppParameterType.INTERNAL_CHORD_ENGINE,
        )
        assert param.key == "MY_PARAM"
        assert param.label == "My Param"
        assert param.label_abreviation == "MP"
        assert param.remappable is False
        assert param.type == AppParameterType.INTERNAL_CHORD_ENGINE
        assert Command.TOGGLE in param.command_mappings

    def test_command_mappings_are_callable(self):
        called = []
        param = AppParameter(
            valid_command_types=[CommandType.ON_OFF],
            command_mappings={
                Command.ON: lambda: called.append("on"),
                Command.OFF: lambda: called.append("off"),
            },
            key="TEST",
        )
        param.command_mappings[Command.ON]()
        param.command_mappings[Command.OFF]()
        assert called == ["on", "off"]


class TestAppParameterType:
    def test_all_types_exist(self):
        assert AppParameterType.MUSIC_ENGINE.value == 1
        assert AppParameterType.CHORD_ENGINE.value == 2
        assert AppParameterType.INTERNAL_CHORD_ENGINE.value == 3
        assert AppParameterType.EXTERNAL_CHORD_ENGINE.value == 4
        assert AppParameterType.UI.value == 5
