class ControlMap():
    name: str
    displayName: str
    inversionMode: str
    bassMode: str
    map: dict[str, str]

    def __init__(self, name: str, displayName: str, inversionMode: str, bassMode: str, map: dict[str, str]):
        self.name = name
        self.displayName = displayName
        self.inversionMode = inversionMode
        self.bassMode = bassMode
        self.map = map