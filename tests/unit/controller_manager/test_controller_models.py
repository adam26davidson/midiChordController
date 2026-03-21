"""Tests for controller manager model classes."""

from controller_manager.models.control_event import ControlEvent
from controller_manager.models.mappable_control_event import MappableControlEvent
from controller_manager.models.mappable_control_type import MappableControlType
from controller_manager.models.polar_orientation import PolarOrientation
from controller_manager.models.raw_control_event import RawControlEvent
from controller_manager.models.raw_control_type import RawControlType


class TestEnums:
    def test_raw_control_type_values(self):
        assert RawControlType.BUTTON.value == 1
        assert RawControlType.PAD.value == 2
        assert RawControlType.ANALOG.value == 3

    def test_mappable_control_type_values(self):
        assert MappableControlType.ON_OFF.value == 1
        assert MappableControlType.POLAR.value == 2
        assert MappableControlType.ANALOG.value == 3

    def test_raw_control_event_values(self):
        assert RawControlEvent.ON is not None
        assert RawControlEvent.OFF is not None
        assert RawControlEvent.UPDATE is not None

    def test_mappable_control_event_values(self):
        assert MappableControlEvent.ON is not None
        assert MappableControlEvent.OFF is not None
        assert MappableControlEvent.UPDATE is not None
        assert MappableControlEvent.POSITIVE is not None
        assert MappableControlEvent.NEGATIVE is not None


class TestPolarOrientation:
    def test_horizontal_raw_events(self):
        events = PolarOrientation.HORIZONTAL.get_raw_control_events()
        assert RawControlEvent.UP in events
        assert RawControlEvent.DOWN in events

    def test_vertical_raw_events(self):
        events = PolarOrientation.VERTICAL.get_raw_control_events()
        assert RawControlEvent.LEFT in events
        assert RawControlEvent.RIGHT in events


class TestControlEvent:
    def test_construction(self):
        event = ControlEvent(
            control_key="btn_south",
            event=MappableControlEvent.ON,
            controller_id="ctrl1",
            value=None,
        )
        assert event.control_key == "btn_south"
        assert event.event == MappableControlEvent.ON
        assert event.controller_id == "ctrl1"
        assert event.value is None

    def test_construction_with_value(self):
        event = ControlEvent(
            control_key="axis_lx",
            event=MappableControlEvent.UPDATE,
            controller_id="ctrl1",
            value=0.75,
        )
        assert event.value == 0.75
