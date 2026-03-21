from models.appParameter import AppParameter
from models.command import Command
from models.commandType import CommandType
from musicEngine.chordEngine.externalChordEngine import ExternalChordEngine
from musicEngine.chordEngine.internalChordEngine import InternalChordEngine
from redux import store
from redux import utils as reduxUtils
from redux.actions import controllerCoupler as ccActions

from .midi import Midi
from .rhythmEngine import RhythmEngine


class MusicEngine:

    def __init__(self):
        self.internalChordEngine = InternalChordEngine()
        self.externalChordEngine = ExternalChordEngine()
        self.rhythmEngine = RhythmEngine()
        self.midi = Midi()

        self.processControllerEvents = True

        self.midi.subscribe(self.externalChordEngine.handleMidiMessage)
        self.internalChordEngine.subscribe(self.rhythmEngine.handleMessage)
        self.externalChordEngine.subscribe(self.rhythmEngine.handleMessage)
        self.rhythmEngine.subscribe(self.midi.handleMessage)

        reduxUtils.addAppParameters(self.getParameters())

        store.dispatch(ccActions.musicEngineAppParametersLoaded())

    def start(self):
        self.externalChordEngine.start()
        self.midi.start()

    def getParameters(self):
        parameters = [
            AppParameter(
                validCommandTypes = [CommandType.ANALOG],
                commandMappings = {
                    Command.UPDATE: self.midi.setAfterTouch
                },
                key = "AFTERTOUCH",
                label = "Aftertouch",
                labelAbreviation="AT",
            )
        ]

        for cc in range(1, 128):
            parameters.append(
                AppParameter(
                    validCommandTypes = [CommandType.ANALOG],
                    commandMappings = {
                        Command.UPDATE: self.midi.getCCSetter(cc)
                    },
                    key = f"MIDI_CC_{cc}",
                    label = f"MIDI CC {cc}",
                    labelAbreviation=f"CC{cc}",
                )
            )

        return parameters
