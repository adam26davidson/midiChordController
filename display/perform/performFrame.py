from models.appParameter import AppParameter
from models.command import Command
from models.commandType import CommandType
from redux import store, utils as ReduxUtils
from ..chordDisplay import ChordDisplay
from .controlDisplay.controlDisplay import ControlDisplay
from .keyboard import Keyboard
from .inversion import Inversion
from .spread import Spread
from .textDisplay import TextDisplay
from pyrsistent import thaw
import tkinter as tk


class PerformFrame(tk.Frame):

    height = 480
    width = 800

    def __init__(self, container):
        super().__init__(container, highlightthickness=0, relief="flat", bg="#000000")

        self.state = {
            'settingIndex': -1,
            'settingName': '',
            'settingLoading': False,
            'controllerName': 'Not Connected',

            'chordType': {'notes': [], 'root': 0},
            'shadowChordNotes': [],
            'playingChordNotes': [],
            'shadowBassNote': 48,
            'playingBassNote': 0,
            'chordOctave': 0,
            'voiceCount': 0,

            'inversionThumbValue': 0,
            'inversionMode': 'continuous',
            'inversionLock': False,
            'hold': False,
            'bassThumbValue': 0,
            'bassMode': 'incremental',

            'bassPosition': 0,
            'bassRange': 4,
            'inversion': 0,
            'inversionRange': 4,

            'key': 0,
            'scale': [],
            'alternate': 'none',
            'modulationSide': 'none'
        }

        self.keyboard = Keyboard(master=self)
        self.spread = Spread(master=self)
        self.inversion = Inversion(master=self)
        self.bassPosition = Inversion(master=self)
        self.chordTextFrame = tk.Frame(self, bg="#000000")
        self.chordTextFrame.pack(side="right")
        self.chordDisplay = ChordDisplay(master=self.chordTextFrame)
        self.textDisplay = TextDisplay(master=self.chordTextFrame)
        self.controlDisplay = ControlDisplay(master=self)

        self.grid(row=0, column=0, sticky='nsew')

        ReduxUtils.addAppParameters(self.getParameters())

        store.subscribe(self.__handleStoreUpdate)

    def __handleStoreUpdate(self):
        state = store.get_state()
        meState = thaw(state['musicEngine'])
        cState = thaw(state['controllerManager'])

        if meState['chordShadow'] != self.state['shadowChordNotes']:
            self.__setChordShadow(meState['chordShadow'])
        if meState['chordNotes'] != self.state['playingChordNotes']:
            if len(meState['chordNotes']) > 0:
                self.__playChord(meState['chordNotes'])
            else:
                self.__stopChord(self.state['playingChordNotes'])
        if meState['bassShadow'] != self.state['shadowBassNote']:
            self.__setBassShadow(meState['bassShadow'])
        if meState['bassNote'] != self.state['playingBassNote']:
            if meState['bassNote'] is not None:
                self.__playBass(meState['bassNote'])
            else:
                self.__stopBass(self.state['playingBassNote'])
        if meState['chordType']['chord'] != self.state['chordType']['notes'] or \
                meState['chordType']['root'] != self.state['chordType']['root']:
            self.__setChord(meState['chordType']['chord'],
                            meState['chordType']['root'])
        if meState['inversion'] != self.state['inversion']:
            self.__setInversion(meState['inversion'])
        if meState['bassPosition'] != self.state['bassPosition']:
            self.__setBassPosition(meState['bassPosition'])
        if meState['inversionRange'] != self.state['inversionRange']:
            self.__setInversionRange(
                meState['inversionRange'], meState['inversion'])
        if meState['bassRange'] != self.state['bassRange']:
            self.__setBassRange(meState['bassRange'], meState['bassPosition'])
        if meState['key'] != self.state['key']:
            self.__setKey(meState['key'])
        if meState['scale'] != self.state['scale']:
            self.__setScale(meState['scale'])
        if meState['modulation']['side'] != self.state['modulationSide']:
            self.__setModulation(
                meState['modulation']['scale'], meState['modulation']['side'])
        if meState['setting'] != self.state['settingIndex'] and len(meState['settingsList']) > 0:
            self.state['settingName'] = meState['settingsList'][meState['setting']]
            self.state['settingIndex'] = meState['setting']
            self.__setSetting(self.state['settingName'])
            print('setting name: ' + self.state['settingName'])
        if meState['settingLoading'] != self.state['settingLoading']:
            if meState['settingLoading']:
                self.__setSettingLoading()
            else:
                self.state['settingLoading'] = False
                self.__setSetting(self.state['settingName'])
        if meState['hold'] != self.state['hold']:
            self.state['hold'] = meState['hold']
            self.__setHold(self.state['hold'])
        if meState['inversionLock'] != self.state['inversionLock']:
            self.state['inversionLock'] = meState['inversionLock']
            self.__setInversionLock(self.state['inversionLock'])
        if meState['chordOctave'] != self.state['chordOctave']:
            self.state['chordOctave'] = meState['chordOctave']
            self.__setOctave(self.state['chordOctave'])
        if meState['voiceCount'] != self.state['voiceCount']:
            self.state['voiceCount'] = meState['voiceCount']
            self.__setVoiceCount(self.state['voiceCount'])

        meMap = None
        primary = None
        for controller in cState['controllers']:
            if controller['role'] == 'primary':
                primary = controller
                meMap = controller['meMap']
                break

        if meMap:
            if meMap['inversionMode'] != self.state['inversionMode']:
                self.state['inversionMode'] = meMap['inversionMode']
            if meMap['bassMode'] != self.state['bassMode']:
                self.state['bassMode'] = meMap['bassMode']
        if primary:
            if primary['name'] != self.state['controllerName']:
                self.state['controllerName'] = primary['name']
                self.__setController(primary['name'])

    # def handleControllerEvent(self, event):
    #     meMap = ReduxUtils.getActiveMeMap()
    #     if event['name'] in meMap.keys():
    #         if self.state['inversionMode'] == 'continuous' and \
    #                 meMap[event['name']] == 'UPDATE_INVERSION':
    #             self.__storeInversionThumb(event['value'])
    #         elif self.state['bassMode'] == 'continuous' and \
    #                 meMap[event['name']] == 'UPDATE_BASS_POSITION':
    #             self.__storeBassPositionThumb(event['value'])
    
    def getParameters(self):
        parameters = [
            AppParameter(
                validCommandTypes=[CommandType.ANALOG],
                commandMappings={Command.UPDATE: self.__storeInversionThumb},
                key="UI_INVERSION_THUMB",
                remappable=False
            ),
            AppParameter(
                validCommandTypes=[CommandType.ANALOG],
                commandMappings={Command.UPDATE: self.__storeBassPositionThumb},
                key="UI_BASS_THUMB",
                remappable=False
            )
        ]
        return parameters

    def updateFrame(self):
        if not self.state['inversionLock']:
            self.__setInversionThumb()
        if self.state['bassMode'] == 'continuous':
            self.__setBassPositionThumb()
        self.chordDisplay.runAnimationStep()

    def __setController(self, text):
        self.textDisplay.setController(text)

    def __setSettingLoading(self):
        self.state['settingLoading'] = True
        self.textDisplay.setSetting('Loading...')

    def __setSetting(self, text):
        if not self.state['settingLoading']:
            self.textDisplay.setSetting(text)

    def __setKey(self, key):
        self.state['key'] = key
        self.chordDisplay.setKey(key)

    def __setScale(self, scale):
        self.state['scale'] = scale
        self.chordDisplay.setScale(scale)

    def __setInversionRange(self, range, inversion):
        self.state['inversionRange'] = range
        self.state['inversion'] = inversion
        self.inversion.setMax(range, inversion)

    def __setInversion(self, inversion):
        self.state['inversion'] = inversion
        self.inversion.setActiveRegion(inversion, self.state['inversionMode'])

    def __storeInversionThumb(self, value):
        self.state['inversionThumbValue'] = value

    def __setInversionThumb(self):
        self.inversion.positionThumb(self.state['inversionThumbValue'])

    def __setBassRange(self, range, position):
        self.state['bassRange'] = range
        self.state['bassPosition'] = position
        self.bassPosition.setMax(range, position)

    def __setBassPosition(self, position):
        self.state['bassPosition'] = position
        self.bassPosition.setActiveRegion(position, self.state['bassMode'])

    def __storeBassPositionThumb(self, value):
        self.state['bassThumbValue'] = value

    def __setBassPositionThumb(self):
        self.bassPosition.positionThumb(self.state['bassThumbValue'])

    def __stopChordShadow(self):
        resetNotes = []
        for note in self.state['shadowChordNotes']:
            if note != self.state['shadowBassNote']:
                resetNotes.append(note)
        self.keyboard.reset(resetNotes)
        # self.state['shadowChordNotes'] = []

    def __stopBassShadow(self):
        noteInPlayingChord = self.state['playingChordNotes'].count(
            self.state['shadowBassNote']) != 0
        noteInShadowChord = self.state['shadowChordNotes'].count(
            self.state['shadowBassNote']) != 0
        if (not noteInPlayingChord) and (not noteInShadowChord)  \
                and self.state['shadowBassNote'] is not None:
            self.keyboard.reset([self.state['shadowBassNote']])
        # self.state['shadowBassNote'] = None

    def __setChord(self, chord, root):
        self.state['chordType'] = {'notes': chord, 'root': root}
        self.keyboard.setChord(chord, root)
        self.chordDisplay.setChord(chord, root)

    def __playChord(self, notes):
        self.__stopChordShadow()
        self.keyboard.play(notes)
        self.state['playingChordNotes'] = notes
        self.chordDisplay.playChord()

    def __playBass(self, note):
        self.__stopBassShadow()
        self.keyboard.play([note])
        self.chordDisplay.playBass(note)
        self.state['playingBassNote'] = note

    def __stopChord(self, notes):
        self.state['shadowChordNotes'] = notes
        self.keyboard.setShadow(notes)
        self.state['playingChordNotes'] = []
        self.chordDisplay.setChordShadow()

    def __stopBass(self, note):
        if self.state['playingChordNotes'].count(note) == 0:
            self.keyboard.setShadow([note])
        self.chordDisplay.setBassShadow(note)
        self.state['shadowBassNote'] = note
        self.state['playingBassNote'] = None

    def __setChordShadow(self, notes):
        self.keyboard.reset(self.state['shadowChordNotes'])
        self.state['shadowChordNotes'] = notes
        self.keyboard.setShadow(notes)
        self.chordDisplay.setChordShadow()

    def __setBassShadow(self, note):
        self.__stopBassShadow()
        self.state['shadowBassNote'] = note
        noteInPlayingChord = self.state['playingChordNotes'].count(note) != 0
        if not noteInPlayingChord:
            self.keyboard.setShadow([note])
        self.chordDisplay.setBassShadow(note)

    def __setModulation(self, newScale, side):
        self.state['modulationSide'] = side
        self.chordDisplay.setModulation(newScale, side)

    def __setHold(self, hold):
        self.textDisplay.setHold(hold)

    def __setInversionLock(self, inversionLock):
        self.textDisplay.setInversionLock(inversionLock)

    def __setOctave(self, octave):
        self.textDisplay.setOctave(octave)

    def __setVoiceCount(self, voiceCount):
        self.textDisplay.setVoices(voiceCount)
