
from controllerManager.models.mappableControlType import MappableControlType

from .mappableControlEvent import MappableControlEvent
from .rawControlConfig import RawControlConfig
from .rawControlEvent import RawControlEvent
from .rawControlType import RawControlType

RAW_ON_EVENTS = [RawControlEvent.UP, RawControlEvent.DOWN, RawControlEvent.LEFT, RawControlEvent.RIGHT, RawControlEvent.ON]
RAW_DIRECTIONAL_EVENTS = [RawControlEvent.UP, RawControlEvent.DOWN, RawControlEvent.LEFT, RawControlEvent.RIGHT]

class RawControl:
    key: str
    label: str
    evDevKey: int
    type: RawControlType
    config: RawControlConfig

    def __init__(
            self,
            key: str,
            label:str,
            evDevKey: str,
            type: RawControlType,
            config: RawControlConfig = None):
        self.key = key
        self.label = label
        self.evDevKey = evDevKey
        self.type = type
        self.config = config


    def getMappableControlKeys(self,
                               mappableControlType: MappableControlType = None,
                               event: RawControlEvent = None
                               ) -> list[str]:

        if self.type == RawControlType.BUTTON:
            return [self.key]

        if mappableControlType == MappableControlType.ON_OFF:

            if event in RAW_DIRECTIONAL_EVENTS:
                return [self.key + "_" + event.name]

            if event == RawControlEvent.OFF:
                keys = []
                for polarEvent in self.config.polarEventMap.values():
                    if polarEvent != RawControlEvent.OFF:
                        keys.append(self.key + "_" + polarEvent.name)
                return keys

        elif mappableControlType == MappableControlType.POLAR:
            if self.type == RawControlType.ANALOG:
                return [self.key + "_" + MappableControlType.POLAR.name]
            if self.type == RawControlType.PAD:
                return [self.key]

        elif mappableControlType == MappableControlType.ANALOG:
            return [self.key]
        else:
            print(f"no mappable control keys found for raw control: {self.key} : {self.type} : {mappableControlType} : {event}")
            return []
        return None


    def getMappableControlEvent(self,
                                mappableControlType: MappableControlType = None,
                                event: RawControlEvent = None
                                ) -> MappableControlEvent:

        if event == RawControlEvent.OFF:
            return MappableControlEvent.OFF

        if mappableControlType == MappableControlType.ON_OFF and event in RAW_ON_EVENTS:
            return MappableControlEvent.ON

        if mappableControlType == MappableControlType.POLAR:

            if event in [RawControlEvent.UP, RawControlEvent.RIGHT]:
                return MappableControlEvent.POSITIVE

            if event in [RawControlEvent.DOWN, RawControlEvent.LEFT]:
                return MappableControlEvent.NEGATIVE

        elif mappableControlType == MappableControlType.ANALOG:
            return MappableControlEvent.UPDATE
        else:
            print(f"no mappable control event found for raw control: {self.key} : {self.type} : {mappableControlType} : {event}")
            return None
        return None

