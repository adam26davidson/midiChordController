"""Tests for controller manager model classes."""

from controller_manager.models.control_event import ControlEvent
from controller_manager.models.mappable_control_event import MappableControlEvent
from controller_manager.models.polar_orientation import PolarOrientation
from controller_manager.models.raw_control_event import RawControlEvent


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
