from models.command import Command
from models.command_type import CommandType


class TestCommandTypeCommands:
    def test_on_off_returns_on_and_off(self):
        assert CommandType.ON_OFF.commands() == [Command.ON, Command.OFF]

    def test_toggle_returns_toggle(self):
        assert CommandType.TOGGLE.commands() == [Command.TOGGLE]

    def test_incremental_returns_increment_decrement(self):
        assert CommandType.INCREMENTAL.commands() == [Command.INCREMENT, Command.DECREMENT]

    def test_analog_returns_update(self):
        assert CommandType.ANALOG.commands() == [Command.UPDATE]


class TestCommandTypeLabel:
    def test_on_off_label(self):
        assert CommandType.ON_OFF.label() == "On/Off"

    def test_toggle_label(self):
        assert CommandType.TOGGLE.label() == "Toggle"

    def test_incremental_label(self):
        assert CommandType.INCREMENTAL.label() == "Increment/Decrement"

    def test_analog_label(self):
        assert CommandType.ANALOG.label() == "Analog"
