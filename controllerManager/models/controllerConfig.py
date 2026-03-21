
from .rawControl import RawControl


class ControllerConfig:
    name: str
    vendor: int
    product: int
    meMap: str
    uiMap: str
    compatibleMeMaps: list[str]
    controls: dict[str, list[RawControl]]

    def __init__(
            self,
            name: str,
            vendor: int,
            product: int,
            meMap: str,
            uiMap: str,
            compatibleMeMaps: list[str],
            controls: dict[str, list[RawControl]]):
        self.name = name
        self.vendor = vendor
        self.product = product
        self.meMap = meMap
        self.uiMap = uiMap
        self.compatibleMeMaps = compatibleMeMaps
        self.controls = controls

