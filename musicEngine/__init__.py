from .chordEngine import ChordEngine
from .chordEngine.controlState import ChordButton
from .rhythmEngine import RhythmEngine
from .midi import Midi
from redux import store
from redux import utils as reduxUtils
from ..models.appParameter import AppParameter
from ..models.commandType import CommandType
from ..models.commandMapping import CommandMapping
from ..models.command import Command
from pyrsistent import thaw


class MusicEngine():

    def __init__(self):
        self.chordEngine = ChordEngine()
        self.rhythmEngine = RhythmEngine()
        self.midi = Midi()

        self.processControllerEvents = True

        self.chordEngine.subscribe(self.rhythmEngine.handleMessage)
        self.rhythmEngine.subscribe(self.midi.handleMessage)

        store.subscribe(self.__handleStoreUpdate)

        reduxUtils.addAppParameters(self.getParameters())

    def start(self):
        self.midi.start()

    def controllerEventHandler(self, event):
        if (self.processControllerEvents):
            controllers = store.get_state()['controllerManager']['controllers']
            meMap = None
            for controller in controllers:
                if controller['role'] == 'primary':
                    meMap = controller['meMap']['map']

            if (event['name'] in meMap.keys()):
                command = meMap[event['name']]
                if 'value' in event.keys():
                    self.commandMap[command](event['value'])
                else:
                    self.commandMap[command]()
    
    def __handleStoreUpdate(self):
        state = store.get_state()
        displayState = thaw(state['display'])

        # if (displayState['activeFrame'] == "PERFORM"):
        #     self.processControllerEvents = True
        # else:
        #     self.processControllerEvents = False

    def getParameters(self):
        return [
            AppParameter(
                validCommandTypes = [CommandType.ON_OFF],
                commandMappings = {
                    Command.ON: lambda: self.chordEngine.chordButtonOn(ChordButton.SOUTH), 
                    Command.OFF: lambda: self.chordEngine.chordButtonOff(ChordButton.SOUTH)
                },
                key = "SOUTH_CHORD",
                label = "South Chord",
                labelAbreviation="S",
            ),
            AppParameter(
                validCommandTypes = [CommandType.ON_OFF],
                commandMappings = {
                    Command.ON: lambda: self.chordEngine.chordButtonOn(ChordButton.WEST), 
                    Command.OFF: lambda: self.chordEngine.chordButtonOff(ChordButton.WEST)
                },
                key = "WEST_CHORD",
                label = "West Chord",
                labelAbreviation="W",
            ),
            AppParameter(
                validCommandTypes = [CommandType.ON_OFF],
                commandMappings = {
                    Command.ON: lambda: self.chordEngine.chordButtonOn(ChordButton.NORTH), 
                    Command.OFF: lambda: self.chordEngine.chordButtonOff(ChordButton.NORTH)
                },
                key = "NORTH_CHORD",
                label = "North Chord",
                labelAbreviation="N",
            ),
            AppParameter(
                validCommandTypes = [CommandType.ON_OFF],
                commandMappings = {
                    Command.ON: lambda: self.chordEngine.chordButtonOn(ChordButton.EAST), 
                    Command.OFF: lambda: self.chordEngine.chordButtonOff(ChordButton.EAST)
                },
                key = "EAST_CHORD",
                label = "East Chord",
                labelAbreviation="E",
            ),
            AppParameter(
                validCommandTypes = [CommandType.ON_OFF],
                commandMappings = {
                    Command.ON: lambda: self.chordEngine.setSecondary('left'), 
                    Command.OFF: lambda: self.chordEngine.setSecondary('none')
                },
                key = "LEFT_SECONDARY",
                label = "Secondary 1",
                labelAbreviation="S1",
            ),
            AppParameter(
                validCommandTypes = [CommandType.ON_OFF],
                commandMappings = {
                    Command.ON: lambda: self.chordEngine.setSecondary('right'), 
                    Command.OFF: lambda: self.chordEngine.setSecondary('none')
                },
                key = "RIGHT_SECONDARY",
                label = "Secondary 2",
                labelAbreviation="S2",
            ),
            AppParameter(
                validCommandTypes = [CommandType.ON_OFF],
                commandMappings = {
                    Command.ON: self.chordEngine.playBass, 
                    Command.OFF: self.chordEngine.stopBass
                },
                key = "BASS",
                label = "Bass",
                labelAbreviation="B",
            ),
            AppParameter(
                validCommandTypes = [CommandType.ON_OFF],
                commandMappings = {
                    Command.ON: lambda: self.chordEngine.setModulation('left'), 
                    Command.OFF: lambda: self.chordEngine.setModulation('none')
                },
                key = "LEFT_MODULATION",
                label = "Modulation 1",
                labelAbreviation="M1",
            ),
            AppParameter(
                validCommandTypes = [CommandType.ON_OFF],
                commandMappings = {
                    Command.ON: lambda: self.chordEngine.setModulation('right'), 
                    Command.OFF: lambda: self.chordEngine.setModulation('none')
                },
                key = "RIGHT_MODULATION",
                label = "Modulation 2",
                labelAbreviation="M2",
            ),
            AppParameter(
                validCommandTypes = [CommandType.TOGGLE],
                commandMappings = {
                    Command.TOGGLE: self.chordEngine.toggleInversionLock
                },
                key = "INVERSION_LOCK",
                label = "Inversion Lock",
                labelAbreviation="IL",
            ),
            AppParameter(
                validCommandTypes = [CommandType.TOGGLE],
                commandMappings = {
                    Command.TOGGLE: self.chordEngine.toggleHold
                },
                key = "HOLD",
                label = "Hold",
                labelAbreviation="H",
            ),
            AppParameter(
                validCommandTypes = [CommandType.ON_OFF],
                commandMappings = {
                    Command.ON: lambda: self.chordEngine.setAlternate(True), 
                    Command.OFF: lambda: self.chordEngine.setAlternate(False)
                },
                key = "ALTERNATE",
                label = "Alternate",
                labelAbreviation="A",
            ),
            AppParameter(
                validCommandTypes = [CommandType.INCREMENTAL],
                commandMappings = {
                    Command.INCREMENT: self.chordEngine.incrementChordOctave, 
                    Command.DECREMENT: self.chordEngine.decrementChordOctave
                },
                key = "OCTAVE",
                label = "Octave",
                labelAbreviation="O",
            ),
            AppParameter(
                validCommandTypes = [CommandType.INCREMENTAL],
                commandMappings = {
                    Command.INCREMENT: self.chordEngine.incrementVoiceCount, 
                    Command.DECREMENT: self.chordEngine.decrementVoiceCount
                },
                key = "VOICE_COUNT",
                label = "Voice Count",
                labelAbreviation="V",
            ),
            AppParameter(
                validCommandTypes = [CommandType.INCREMENTAL],
                commandMappings = {
                    Command.INCREMENT: self.chordEngine.incrementKey, 
                    Command.DECREMENT: self.chordEngine.decrementKey
                },
                key = "KEY",
                label = "Transpose",
                labelAbreviation="T",
            ),
            AppParameter(
                validCommandTypes = [CommandType.INCREMENTAL],
                commandMappings = {
                    Command.INCREMENT: self.chordEngine.incrementSpread, 
                    Command.DECREMENT: self.chordEngine.decrementSpread
                },
                key = "SPREAD",
                label = "Spread",
                labelAbreviation="S",
            ),
            AppParameter(
                validCommandTypes = [CommandType.INCREMENTAL],
                commandMappings = {
                    Command.INCREMENT: self.chordEngine.incrementSetting, 
                    Command.DECREMENT: self.chordEngine.decrementSetting
                },
                key = "SETTING",
                label = "Patch",
                labelAbreviation="P",
            ),
            AppParameter(
                validCommandTypes = [CommandType.ANALOG, CommandType.INCREMENTAL],
                commandMappings = {
                    Command.UPDATE: self.chordEngine.setAnalogBassPosition,
                    Command.INCREMENT: self.chordEngine.incrementBassPosition,
                    Command.DECREMENT: self.chordEngine.decrementBassPosition
                },
                key = "BASS_POSITION",
                label = "Bass Position",
                labelAbreviation="BP",
            ),
            AppParameter(
                validCommandTypes = [CommandType.ANALOG, CommandType.INCREMENTAL],
                commandMappings = {
                    Command.UPDATE: self.chordEngine.setAnalogInversion,
                    Command.INCREMENT: self.chordEngine.incrementInversion,
                    Command.DECREMENT: self.chordEngine.decrementInversion
                },
                key = "INVERSION",
                label = "Inversion",
                labelAbreviation="I",
            ),
            AppParameter(
                validCommandTypes = [CommandType.ANALOG],
                commandMappings = {
                    Command.UPDATE: self.midi.setAfterTouch
                },
                key = "AFTERTOUCH",
                label = "Aftertouch",
                labelAbreviation="AT",
            ),
            AppParameter(
                validCommandTypes = [CommandType.ANALOG],
                commandMappings = {
                    Command.UPDATE: self.midi.getCCSetter(1)
                },
                key = "MIDI_CC_1",
                label = "MIDI CC 1",
                labelAbreviation="CC1",
            ),
            AppParameter(
                validCommandTypes = [CommandType.ANALOG],
                commandMappings = {
                    Command.UPDATE: self.midi.getCCSetter(2)
                },
                key = "MIDI_CC_2",
                label = "MIDI CC 2",
                labelAbreviation="CC2",
            )
        ]
