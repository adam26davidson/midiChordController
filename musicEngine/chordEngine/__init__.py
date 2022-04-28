from .modules.dualChord import DualChord
from .modules.modulation import Modulation
from .modules.parseSecondaries import parseSecondaries
from utils import findAllOctavesInRange
from constants import SETTINGS, MAX_INVERSION_RANGE, MAX_OCTAVE_SHIFT, \
    MAX_BASS_RANGE, SPREAD_STEPS_PER_OCTAVE, MAX_SPREAD_OCTAVES, \
    MAX_VOICE_COUNT, INVERSION_SNAP
from redux import store
from redux.actions import musicEngine as actions
import math


class ChordEngine:
    def __init__(self, settingIndex=0):

        self.setting = SETTINGS[settingIndex]
        settingsList = [s['name'] for s in SETTINGS]
        store.dispatch(actions.changeSettingsList(settingsList))
        self.callbacks = []
        self.state = {
            'settingIndex': settingIndex,
            'loadingSetting': False,

            'scale': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            'scaleNotes': [],
            'allScaleNotes': [],

            # 0 is C, 1 is C# etc.
            'key': 0,
            'inversionRange': 4,

            # can be "incremental" or "continuous"
            'inversionMode': 'incremental',
            'bassRange': 4,

            # can be "incremental" or "continuous"
            'bassMode': 'incremental',
            'inversion': 0,
            'bassPosition': 0,
            'chordOctave': 0,
            'spread': SPREAD_STEPS_PER_OCTAVE,

            'voiceCount': 5,

            # can be 'max' or 'absolute'
            'voiceCountMode': 'absolute',
            'hold': False,
            'inversionLock': False,

            # can be "left", "none", or "right"
            'modulation': 'none',
            # can be "left", "none", or "right"
            'secondary': 'none',
            'alternate': False,

            'rootType': 0,
            'chordType': [],
            'playingChordNotes': [],
            'chordIsPlaying': False,
            'playingBassNote': None,
            'bassIsPlaying': False,
            'activeChord': 'south',
            'chordButtonStates': {
                'north': False,
                'south': False,
                'east': False,
                'west': False,
            },
            'modulationButtonStates': {
                'left': False,
                'right': False
            }
        }
        kAction = actions.changeKey(self.state['key'])
        store.dispatch(kAction)
        iRAction = actions.changeInversionRange(self.state['inversionRange'])
        store.dispatch(iRAction)
        bRAction = actions.changeBassRange(self.state['bassRange'])
        store.dispatch(bRAction)
        iAction = actions.changeInversion(self.state['inversion'])
        store.dispatch(iAction)
        bPAction = actions.changeBassPosition(self.state['bassPosition'])
        store.dispatch(bPAction)

        self.setSetting(self.state['settingIndex'])

    def incrementSetting(self):
        self.setSetting((self.state['settingIndex'] + 1) % len(SETTINGS))

    def decrementSetting(self):
        newIndex = self.state['settingIndex'] - 1
        if (newIndex < 0):
            newIndex = len(SETTINGS) - 1
        self.setSetting(newIndex)

    def setSetting(self, setting):
        self.state['loadingSetting'] = True
        store.dispatch(actions.changeSettingLoading(True))
        self.stopChord(buttonUp=False)
        self.stopBass(buttonUp=False)
        self.state['settingIndex'] = setting
        self.setting = SETTINGS[setting]

        scale = self.setting["scale"]
        self.state['scale'] = scale

        scaleNotes, allScaleNotes = self.__findScaleNotes()
        self.state['scaleNotes'] = scaleNotes
        self.state['allScaleNotes'] = allScaleNotes

        self.chords = {
            "south": DualChord(self.setting["chords"]["south"], scale),
            "west": DualChord(self.setting["chords"]["west"], scale),
            "north": DualChord(self.setting["chords"]["north"], scale),
            "east": DualChord(self.setting["chords"]["east"], scale)
        }

        self.secondaries = parseSecondaries(self.setting["secondaries"])

        self.modulations = {
            "left": Modulation(scale, self.setting["modulations"]["left"]),
            "right": Modulation(scale, self.setting["modulations"]["right"])
        }

        types = self.__getChordType(self.state['activeChord'])
        self.state['chordType'], self.state['rootType'] = types

        store.dispatch(actions.changeSetting(setting))
        store.dispatch(actions.changeScale(scale))
        store.dispatch(actions.changeChordType({
            'chord': self.state['chordType'],
            'root': self.state['rootType']
        }))
        shadowChord = self.__getChord(self.state['activeChord'])
        store.dispatch(actions.changeChordShadow(shadowChord))
        store.dispatch(actions.changeBassShadow(self.__getBass()))

        store.dispatch(actions.changeSettingLoading(False))
        self.state['loadingSetting'] = False

    def playChord(self, button=None, fromButton=False):
        if fromButton:
            self.state['chordButtonStates'][button] = True
            self.state['activeChord'] = button
        self.__setChordType()
        self.stopChord(buttonUp=False)
        notes = self.__getChord(button)
        self.__sendNotesOn(notes, player='chord')
        self.__updateBass()
        store.dispatch(actions.playChord(notes))
        self.state['playingChordNotes'] = notes
        self.state['chordIsPlaying'] = True

    def playBass(self):
        self.stopBass(buttonUp=False)
        bassNote = self.__getBass()
        self.__sendNotesOn([bassNote], player='bass')
        store.dispatch(actions.playBass(bassNote))
        self.state['playingBassNote'] = bassNote
        self.state['bassIsPlaying'] = True

    def stopChord(self, button=None, buttonUp=True):
        if button is not None:
            self.state['chordButtonStates'][button] = False
        # dontStop = self.state['chordIsPlaying'] and button is not None \
        #     and button != self.state['activeChord']
        if (not buttonUp or not self.state['hold']):
            if self.state['chordIsPlaying']:
                playingNotes = self.state['playingChordNotes']
                self.__sendNotesOff(playingNotes, player='chord')
                store.dispatch(actions.stopChord())
                self.state['playingChordNotes'] = []
                self.state['chordIsPlaying'] = False
                # for b, isOn in self.state['chordButtonStates'].items():
                #   if isOn:
                #     self.playChord(b)

    def stopBass(self, buttonUp=True):
        if not buttonUp or not self.state['hold']:
            if self.state['bassIsPlaying']:
                playingBass = self.state['playingBassNote']
                self.__sendNotesOff([playingBass], player='bass')
                store.dispatch(actions.stopBass())
                self.state['playingBassNote'] = None
                self.state['bassIsPlaying'] = False

    def setModulation(self, side):
        if self.state['modulation'] != side:
            scale = self.state['scale']
            if side != "none":
                scale = self.modulations[side].applyToScale()
            store.dispatch(actions.changeModulation({
                'scale': scale,
                'side': side
            }))
            self.state['modulation'] = side
            self.__setChordType()
            self.__updateChord()
            self.__updateBass()

    def setSecondary(self, side):
        if self.state['secondary'] != side:
            self.state['secondary'] = side
            self.__setChordType()
            self.__updateChord()
            self.__updateBass()

    def setAlternate(self, alternate):
        if self.state['alternate'] != alternate:
            self.state['alternate'] = alternate
            self.__setChordType()
            self.__updateChord()
            self.__updateBass()

    def incrementInversion(self):
        newInversion = self.state['inversion'] + 1
        if abs(newInversion) <= self.state['inversionRange']:
            self.setInversion(newInversion)

    def decrementInversion(self):
        newInversion = self.state['inversion'] - 1
        if abs(newInversion) <= self.state['inversionRange']:
            self.setInversion(newInversion)

    def setInversion(self, inversion):
        if (not self.state['inversionLock']):
            if inversion != self.state['inversion']:
                range = self.state['inversionRange']
                self.state['inversion'] = max(min(inversion, range), -1*range)
                self.__updateChord()
                iAction = actions.changeInversion(self.state['inversion'])
                store.dispatch(iAction)

    def setAnalogInversion(self, value):
        inversion = self.processInversionValue(value, type='chord')
        self.setInversion(inversion)

    def setAnalogBassPosition(self, value):
        position = self.processInversionValue(value, type='bass')
        self.setBassPosition(position)

    def setInversionRange(self, range):
        range = max(min(range, MAX_INVERSION_RANGE), 0)
        self.state['inversionRange'] = range
        oldInversion = self.state['inversion']
        self.state['inversion'] = max(min(oldInversion, range), -1*range)
        self.__updateChord()
        iAction = actions.changeInversion(self.state['inversion'])
        store.dispatch(iAction)
        irAction = actions.changeInversionRange(self.state['inversionRange'])
        store.dispatch(irAction)

    def incrementBassPosition(self):
        newPosition = self.state['bassPosition'] + 1
        if abs(newPosition) <= self.state['bassRange']:
            self.setBassPosition(newPosition)

    def decrementBassPosition(self):
        newPosition = self.state['bassPosition'] - 1
        if abs(newPosition) <= self.state['bassRange']:
            self.setBassPosition(newPosition)

    def setBassPosition(self, position):
        if position != self.state['bassPosition']:
            range = self.state['bassRange']
            self.state['bassPosition'] = max(min(position, range), -1*range)
            self.__updateBass()
            bAction = actions.changeBassPosition(self.state['bassPosition'])
            store.dispatch(bAction)

    def setBassRange(self, range):
        range = max(min(range, MAX_BASS_RANGE), 0)
        self.state['bassRange'] = range
        oldBP = self.state['bassPosition']
        self.state['bassPosition'] = max(min(oldBP, range), -1*range)
        self.__updateBass()
        store.dispatch(actions.changeInversion(self.state['bassPosition']))
        store.dispatch(actions.changeInversionRange(self.state['bassRange']))

    def setSpread(self, spread):
        maxSpread = SPREAD_STEPS_PER_OCTAVE * MAX_SPREAD_OCTAVES - 1
        spread = max(min(spread, maxSpread), 0)
        self.state['spread'] = spread
        self.__updateChord()
        store.dispatch(actions.changeSpread(self.state['spread']))

    def incrementSpread(self):
        self.setSpread(self.state['spread'] + 1)

    def decrementSpread(self):
        self.setSpread(self.state['spread'] - 1)

    def setKey(self, key):
        key = key % 12
        if self.state['key'] != key:
            self.state['key'] = key
            store.dispatch(actions.changeKey(key))
            self.__setChordType()
            self.__updateChord()
            self.__updateBass()

    def incrementKey(self):
        self.setKey(self.state['key'] + 1)

    def decrementKey(self):
        self.setKey(self.state['key'] + 11)

    def setVoiceCount(self, count):
        count = max(min(count, MAX_VOICE_COUNT), 1)
        self.state['voiceCount'] = count
        self.__updateChord()
        store.dispatch(actions.changeVoiceCount(self.state['voiceCount']))

    def incrementVoiceCount(self):
        self.setVoiceCount(self.state['voiceCount'] + 1)

    def decrementVoiceCount(self):
        self.setVoiceCount(self.state['voiceCount'] - 1)

    def setChordChannel(self, channel):
        channel = max(min(channel, 16), 0)
        self.state['chordChannel'] = channel
        self.__updateChord()
        store.dispatch(actions.changeChordChannel(channel))

    def setBassChannel(self, channel):
        channel = max(min(channel, 16), 0)
        self.state['bassChannel'] = channel
        self.__updateBass()
        store.dispatch(actions.changeBassChannel(channel))

    def setChordOctave(self, octave):
        clamped = max(min(octave, MAX_OCTAVE_SHIFT), -1*MAX_OCTAVE_SHIFT)
        self.state['chordOctave'] = clamped
        self.__updateChord()
        store.dispatch(actions.changeChordOctave(self.state['chordOctave']))

    def incrementChordOctave(self):
        self.setChordOctave(self.state['chordOctave'] + 1)

    def decrementChordOctave(self):
        self.setChordOctave(self.state['chordOctave'] - 1)

    def toggleHold(self):
        if self.state['hold']:
            self.state['hold'] = False
            self.stopChord(buttonUp=False)
            self.stopBass(buttonUp=False)
        else:
            self.state['hold'] = True
        store.dispatch(actions.changeHold(self.state['chordOctave']))

    def toggleInversionLock(self):
        self.state['inversionLock'] = not self.state['inversionLock']
        iAction = actions.changeInversionLock(self.state['inversionLock'])
        store.dispatch(iAction)

    def processInversionValue(self, rawValue, type='chord'):
        maxSteps = self.state['inversionRange']
        if type != 'chord':
            self.state['bassRange']
        lastValue = self.state['inversion']
        if type != 'chord':
            self.state['bassPosition']

        # converts to an integer in the correct inversion range
        def getValue(x):
            return math.floor(((x+1)/2)*((2*maxSteps)+1)) - maxSteps

        # snap processed value back into current window if within snap region
        value = getValue(rawValue)
        snap = (1.0 / (maxSteps + 1)) * INVERSION_SNAP
        if value == lastValue + 1:
            rawValue -= snap
            value = getValue(rawValue)
        if value == lastValue - 1:
            rawValue += snap
            value = getValue(rawValue)

        return value

    def subscribe(self, callback):
        self.callbacks.append(callback)

    def __findScaleNotesForKey(self, key):
        scaleNotes = []
        for note in self.state['scale']:
            scaleNotes.append((note + key) % 12)
        return scaleNotes

    def __findScaleNotes(self):
        scaleNotes = {}
        allScaleNotes = {}
        for key in range(0, 12):
            scaleNotes[key] = self.__findScaleNotesForKey(key)
            allScaleNotes[key] = findAllOctavesInRange(scaleNotes[key])
        return scaleNotes, allScaleNotes

    def __sendNotesOn(self, notes, player):
        message = {
            'type': 'on',
            'notes': notes,
            'player': player
        }
        self.__sendMessage(message)

    def __sendNotesOff(self, notes, player):
        message = {
            'type': 'off',
            'notes': notes,
            'player': player
        }
        self.__sendMessage(message)

    def __sendMessage(self, message):
        for callback in self.callbacks:
            callback(message)

    def __mod12(self, notes):
        newNotes = []
        for note in notes:
            newNotes.append(note % 12)
        return newNotes

    def __getChordType(self, button):
        chord = self.chords[button]
        secState = self.state['secondary']
        # secondary inactive
        if (secState == "none"):
            if (self.state['modulation'] == "none"):
                rootType = chord.getRoot(self.state)
                chordType = chord.getNoteTypes(self.state)
                return chordType, rootType
            else:
                modulation = self.modulations[self.state['modulation']]
                root = chord.getRoot(self.state)
                rootType = modulation.applyOne(root, self.__getScale()) % 12
                rawTypes = chord.getNoteTypes(self.state)
                moddedTypes = modulation.apply(rawTypes, self.__getScale())
                chordType = self.__mod12(moddedTypes)
                return chordType, rootType
        # secondary is active
        else:
            modKey = "default"
            if (self.state['modulation'] == "left"):
                modKey = "leftModulation"
            elif (self.state['modulation'] == "left"):
                modKey = "rightModulation"
            secondary = self.secondaries[secState][button][modKey]
            chordRoot = chord.getRoot(self.state)
            rootType = secondary.getRoot(self.state, chordRoot)
            chordType = secondary.getNoteTypes(self.state, chordRoot)
            chordType.sort()
            return chordType, rootType

    def __setChordType(self):
        chord, root = self.__getChordType(self.state['activeChord'])
        if chord != self.state['chordType'] or root != self.state['rootType']:
            self.state['chordType'], self.state['rootType'] = chord, root
            ctAction = actions.changeChordType({'chord': chord, 'root': root})
            store.dispatch(ctAction)

    def __getChord(self, button):
        secState = self.state['secondary']
        chord = self.chords[button]
        chordNotes = []
        # secondary inactive
        if (secState == "none"):
            if (self.state['modulation'] == "none"):
                chordNotes = chord.getChord(self.state)
            else:
                modulation = self.modulations[self.state['modulation']]
                modlessChord = chord.getChord(self.state)
                chordNotes = modulation.apply(modlessChord, self.__getScale())
        # secondary is active
        else:
            modKey = "default"
            if (self.state['modulation'] == "left"):
                modKey = "leftModulation"
            elif (self.state['modulation'] == "left"):
                modKey = "rightModulation"
            secondary = self.secondaries[secState][button][modKey]
            root = chord.getRoot(self.state)
            chordNotes = secondary.getChord(self.state, root)

        chordAdjustedOctaves = self.__setOctave(chordNotes)
        return chordAdjustedOctaves

    def __setOctave(self, chordNotes):
        return [note + (self.state['chordOctave'] * 12) for note in chordNotes]

    def __getScale(self):
        return self.state['scaleNotes'][self.state['key']]

    def __getBass(self):
        chordLabel = self.state['activeChord']
        secLabel = self.state['secondary']
        chord = self.chords[chordLabel]

        # secondary not active
        if (self.state['secondary'] == "none"):
            if (self.state['modulation'] == "none"):
                return chord.getBass(self.state)
            else:
                modulation = self.modulations[self.state['modulation']]
                bass = chord.getBass(self.state)
                return modulation.applyOne(bass, self.__getScale())
        # secondary is active
        else:
            modKey = "default"
            if (self.state['modulation'] == "left"):
                modKey = "leftModulation"
            elif (self.state['modulation'] == "left"):
                modKey = "rightModulation"

        secondary = self.secondaries[secLabel][chordLabel][modKey]
        return secondary.getBass(self.state, chord.getRoot(self.state))

    def __updateChord(self):
        if (self.state['chordIsPlaying']):
            self.playChord(self.state['activeChord'])
        else:
            notes = self.__getChord(self.state['activeChord'])
            store.dispatch(actions.changeChordShadow(notes))

    def __updateBass(self):
        if (self.state['bassIsPlaying']):
            self.playBass()
        else:
            note = self.__getBass()
            store.dispatch(actions.changeBassShadow(note))
