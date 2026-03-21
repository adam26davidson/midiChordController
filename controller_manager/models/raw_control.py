
from controller_manager.models.mappable_control_type import MappableControlType

from .mappable_control_event import MappableControlEvent
from .raw_control_config import RawControlConfig
from .raw_control_event import RawControlEvent
from .raw_control_type import RawControlType

RAW_ON_EVENTS = [RawControlEvent.UP, RawControlEvent.DOWN, RawControlEvent.LEFT, RawControlEvent.RIGHT, RawControlEvent.ON]
RAW_DIRECTIONAL_EVENTS = [RawControlEvent.UP, RawControlEvent.DOWN, RawControlEvent.LEFT, RawControlEvent.RIGHT]

class RawControl:
    key: str
    label: str
    ev_dev_key: int
    type: RawControlType
    config: RawControlConfig

    def __init__(
            self,
            key: str,
            label:str,
            ev_dev_key: str,
            type: RawControlType,
            config: RawControlConfig = None):
        self.key = key
        self.label = label
        self.ev_dev_key = ev_dev_key
        self.type = type
        self.config = config


    def get_mappable_control_keys(self,
                               mappable_control_type: MappableControlType = None,
                               event: RawControlEvent = None
                               ) -> list[str]:

        if self.type == RawControlType.BUTTON:
            return [self.key]

        if mappable_control_type == MappableControlType.ON_OFF:

            if event in RAW_DIRECTIONAL_EVENTS:
                return [self.key + "_" + event.name]

            if event == RawControlEvent.OFF:
                keys = []
                for polar_event in self.config.polar_event_map.values():
                    if polar_event != RawControlEvent.OFF:
                        keys.append(self.key + "_" + polar_event.name)
                return keys

        elif mappable_control_type == MappableControlType.POLAR:
            if self.type == RawControlType.ANALOG:
                return [self.key + "_" + MappableControlType.POLAR.name]
            if self.type == RawControlType.PAD:
                return [self.key]

        elif mappable_control_type == MappableControlType.ANALOG:
            return [self.key]
        else:
            print(f"no mappable control keys found for raw control: {self.key} : {self.type} : {mappable_control_type} : {event}")
            return []
        return None


    def get_mappable_control_event(self,
                                mappable_control_type: MappableControlType = None,
                                event: RawControlEvent = None
                                ) -> MappableControlEvent:

        if event == RawControlEvent.OFF:
            return MappableControlEvent.OFF

        if mappable_control_type == MappableControlType.ON_OFF and event in RAW_ON_EVENTS:
            return MappableControlEvent.ON

        if mappable_control_type == MappableControlType.POLAR:

            if event in [RawControlEvent.UP, RawControlEvent.RIGHT]:
                return MappableControlEvent.POSITIVE

            if event in [RawControlEvent.DOWN, RawControlEvent.LEFT]:
                return MappableControlEvent.NEGATIVE

        elif mappable_control_type == MappableControlType.ANALOG:
            return MappableControlEvent.UPDATE
        else:
            print(f"no mappable control event found for raw control: {self.key} : {self.type} : {mappable_control_type} : {event}")
            return None
        return None

