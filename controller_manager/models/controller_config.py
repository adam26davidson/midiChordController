
from .raw_control import RawControl


class ControllerConfig:
    name: str
    vendor: int
    product: int
    me_map: str
    ui_map: str
    compatible_me_maps: list[str]
    controls: dict[str, list[RawControl]]

    def __init__(
            self,
            name: str,
            vendor: int,
            product: int,
            me_map: str,
            ui_map: str,
            compatible_me_maps: list[str],
            controls: dict[str, list[RawControl]]):
        self.name = name
        self.vendor = vendor
        self.product = product
        self.me_map = me_map
        self.ui_map = ui_map
        self.compatible_me_maps = compatible_me_maps
        self.controls = controls

