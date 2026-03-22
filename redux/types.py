from __future__ import annotations

from typing import Any, TypedDict


class _ReduxActionRequired(TypedDict):
    type: str


class ReduxAction(_ReduxActionRequired, total=False):
    data: dict[str, Any]


class ChordTypeState(TypedDict):
    chord: list[int]
    root: int


class ModulationState(TypedDict):
    side: str
    scale: list[int]


class ControllerState(TypedDict):
    id: str
    name: str
    role: str
    compatibleMeMaps: list[str]
    meMap: Any
    uiMap: Any


class MusicEngineState(TypedDict):
    chordEngineControl: str

    availableMidiPorts: list[str]
    connectedMidiPort: str
    bassChannel: int
    chordChannel: int
    distributeChannels: bool
    velocity: int
    velocityMode: str
    velocityDeviation: int
    aftertouchMode: str

    strumMode: str
    strumInterval: float
    strumOrder: str

    settingsList: list[str]
    setting: int
    settingLoading: bool
    key: int
    transposeIncrement: int
    scale: list[int]
    spread: int
    inversion: int
    inversionMode: str
    inversionRange: int
    inversionLock: bool
    hold: bool
    bassPosition: int
    bassMode: str
    bassRange: int
    chordOctave: int
    voiceCount: int
    modulation: ModulationState
    secondary: str
    bassNote: int | None
    bassShadow: int
    chordNotes: list[int]
    chordType: ChordTypeState
    chordShadow: list[int]


class ControllerManagerState(TypedDict):
    waitingForConnection: bool
    controllers: list[ControllerState]


class ControllerCouplerState(TypedDict):
    activeControlMap: Any | None
    appParameters: dict[str, Any]
    controls: dict[str, Any]
    musicEngineAppParametersLoaded: bool


class DisplayState(TypedDict):
    activeFrame: str


class RootState(TypedDict):
    controllerManager: ControllerManagerState
    controllerCoupler: ControllerCouplerState
    musicEngine: MusicEngineState
    display: DisplayState
