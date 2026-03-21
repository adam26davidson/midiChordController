from enum import Enum

from controllerManager.models.rawControlEvent import RawControlEvent


class PolarOrientation(Enum):
    HORIZONTAL = 1
    VERTICAL = 2

    def get_raw_control_events(self):
        if self.name == "HORIZONTAL":
            return [RawControlEvent.UP, RawControlEvent.DOWN]
        if self.name == "VERTICAL":
            return [RawControlEvent.LEFT, RawControlEvent.RIGHT]
        return []
