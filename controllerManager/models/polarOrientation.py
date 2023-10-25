from enum import Enum

from controllerManager.models.rawControlEvent import RawControlEvent

class PolarOrientation(Enum):
    HORIZONTAL = 1
    VERTICAL = 2
    
    def getRawControlEvents(self):
        if self.name == "HORIZONTAL":
            return [RawControlEvent.UP, RawControlEvent.DOWN]
        elif self.name == "VERTICAL":
            return [RawControlEvent.LEFT, RawControlEvent.RIGHT]
        else:
            return []