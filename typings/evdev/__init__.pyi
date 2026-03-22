from collections.abc import Iterator

class InputEvent:
    type: int
    code: int
    value: int
    def timestamp(self) -> float: ...

class DeviceInfo:
    vendor: int
    product: int

class InputDevice:
    fd: int
    name: str
    info: DeviceInfo
    uniq: str
    def __init__(self, path: str) -> None: ...
    def read(self) -> Iterator[InputEvent]: ...

def list_devices() -> list[str]: ...
