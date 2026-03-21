import tkinter as tk

from pyrsistent import thaw

from models.appParameter import AppParameter, AppParameterType
from models.command import Command
from models.commandType import CommandType
from redux import store
from redux import utils as redux_utils

from ..chordDisplay import ChordDisplay
from .controlDisplay.controlDisplay import ControlDisplay
from .inversion import Inversion
from .keyboard import Keyboard
from .settingDisplay import SettingDisplay
from .spread import Spread
from .textDisplay import TextDisplay


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
        self.chordTextFrame.pack(side="right", padx=(0, 30))
        self.chordDisplay = ChordDisplay(master=self.chordTextFrame)
        self.textDisplay = TextDisplay(master=self.chordTextFrame)
        self.settingDisplay = SettingDisplay(master=self)
        self.controlDisplay = ControlDisplay(master=self)

        self.grid(row=0, column=0, sticky='nsew')

        redux_utils.add_app_parameters(self.get_parameters())

        store.subscribe(self.__handle_store_update)

    def __handle_store_update(self):
        state = store.get_state()
        me_state = thaw(state['musicEngine'])
        c_state = thaw(state['controllerManager'])

        if me_state['chordShadow'] != self.state['shadowChordNotes']:
            self.after(0, lambda: self.__set_chord_shadow(me_state['chordShadow']))
        if me_state['chordNotes'] != self.state['playingChordNotes']:
            print(f"[PERF_FRAME] chordNotes changed: store={me_state['chordNotes']} local={self.state['playingChordNotes']}", flush=True)
            if len(me_state['chordNotes']) > 0:
                self.after(0, lambda: self.__play_chord(me_state['chordNotes']))
            else:
                self.after(0, lambda: self.__stop_chord(self.state['playingChordNotes']))
        if me_state['inversion'] != self.state['inversion']:
            print(f"[PERF_FRAME] inversion changed: store={me_state['inversion']} local={self.state['inversion']}", flush=True)
        if me_state['bassShadow'] != self.state['shadowBassNote']:
            self.after(0, lambda: self.__set_bass_shadow(me_state['bassShadow']))
        if me_state['bassNote'] != self.state['playingBassNote']:
            if me_state['bassNote'] is not None:
                self.after(0, lambda: self.__play_bass(me_state['bassNote']))
            else:
                self.after(0, lambda: self.__stop_bass(self.state['playingBassNote']))
        if me_state['chordType']['chord'] != self.state['chordType']['notes'] or \
                me_state['chordType']['root'] != self.state['chordType']['root']:
            self.after(0, lambda: self.__set_chord(me_state['chordType']['chord'], me_state['chordType']['root']))
        if me_state['inversion'] != self.state['inversion']:
            self.after(0, lambda: self.__set_inversion(me_state['inversion']))
        if me_state['bassPosition'] != self.state['bassPosition']:
            self.after(0, lambda: self.__set_bass_position(me_state['bassPosition']))
        if me_state['inversionRange'] != self.state['inversionRange']:
            self.after(0, lambda: self.__set_inversion_range(
                me_state['inversionRange'], me_state['inversion']))
        if me_state['bassRange'] != self.state['bassRange']:
            self.after(0, lambda: self.__set_bass_range(me_state['bassRange'], me_state['bassPosition']))
        if me_state['key'] != self.state['key']:
            self.after(0, lambda: self.__set_key(me_state['key']))
        if me_state['scale'] != self.state['scale']:
            self.after(0, lambda: self.__set_scale(me_state['scale']))
        if me_state['modulation']['side'] != self.state['modulationSide']:
            self.after(0, lambda: self.__set_modulation(
                me_state['modulation']['scale'], me_state['modulation']['side']))
        if me_state['setting'] != self.state['settingIndex'] and len(me_state['settingsList']) > 0:
            self.state['settingName'] = me_state['settingsList'][me_state['setting']]
            self.state['settingIndex'] = me_state['setting']
            self.after(0, lambda: self.__set_setting(self.state['settingName']))
            print('setting name: ' + self.state['settingName'])
        if me_state['settingLoading'] != self.state['settingLoading']:
            if me_state['settingLoading']:
                self.after(0, lambda: self.__set_setting_loading())
            else:
                self.state['settingLoading'] = False
                self.after(0, lambda: self.__set_setting(self.state['settingName']))
        if me_state['hold'] != self.state['hold']:
            self.state['hold'] = me_state['hold']
            self.after(0, lambda: self.__set_hold(self.state['hold']))
        if me_state['inversionLock'] != self.state['inversionLock']:
            self.state['inversionLock'] = me_state['inversionLock']
            self.after(0, lambda: self.__set_inversion_lock(self.state['inversionLock']))
        if me_state['chordOctave'] != self.state['chordOctave']:
            self.state['chordOctave'] = me_state['chordOctave']
            self.after(0, lambda: self.__set_octave(self.state['chordOctave']))
        if me_state['voiceCount'] != self.state['voiceCount']:
            self.state['voiceCount'] = me_state['voiceCount']
            self.after(0, lambda: self.__set_voice_count(self.state['voiceCount']))

        me_map = None
        primary = None
        for controller in c_state['controllers']:
            if controller['role'] == 'primary':
                primary = controller
                me_map = controller['meMap']
                break

        if me_map:
            if me_map['inversionMode'] != self.state['inversionMode']:
                self.state['inversionMode'] = me_map['inversionMode']
            if me_map['bassMode'] != self.state['bassMode']:
                self.state['bassMode'] = me_map['bassMode']
        if primary and primary['name'] != self.state['controllerName']:
            self.state['controllerName'] = primary['name']
                #self.__set_controller(primary['name'])

    def get_parameters(self):
        parameters = [
            AppParameter(
                valid_command_types=[CommandType.ANALOG],
                command_mappings={Command.UPDATE: self.__store_inversion_thumb},
                key="UI_INVERSION_THUMB",
                remappable=False,
                type=AppParameterType.UI
            ),
            AppParameter(
                valid_command_types=[CommandType.ANALOG],
                command_mappings={Command.UPDATE: self.__store_bass_position_thumb},
                key="UI_BASS_THUMB",
                remappable=False,
                type=AppParameterType.UI
            )
        ]
        return parameters

    def update_frame(self):
        if not self.state['inversionLock']:
            self.__set_inversion_thumb()
        if self.state['bassMode'] == 'continuous':
            self.__set_bass_position_thumb()
        self.chordDisplay.run_animation_step()

    def __set_controller(self, text):
        self.textDisplay.set_controller(text)

    def __set_setting_loading(self):
        self.state['settingLoading'] = True
        self.settingDisplay.set_setting('Loading...')

    def __set_setting(self, text):
        if not self.state['settingLoading']:
            self.settingDisplay.set_setting(text)

    def __set_key(self, key):
        self.state['key'] = key
        self.chordDisplay.set_key(key)

    def __set_scale(self, scale):
        self.state['scale'] = scale
        self.chordDisplay.set_scale(scale)

    def __set_inversion_range(self, range, inversion):
        self.state['inversionRange'] = range
        self.state['inversion'] = inversion
        self.inversion.set_max(range, inversion)

    def __set_inversion(self, inversion):
        self.state['inversion'] = inversion
        self.inversion.set_active_region(inversion, self.state['inversionMode'])

    def __store_inversion_thumb(self, value):
        self.state['inversionThumbValue'] = value

    def __set_inversion_thumb(self):
        self.inversion.position_thumb(self.state['inversionThumbValue'])

    def __set_bass_range(self, range, position):
        self.state['bassRange'] = range
        self.state['bassPosition'] = position
        self.bassPosition.set_max(range, position)

    def __set_bass_position(self, position):
        self.state['bassPosition'] = position
        self.bassPosition.set_active_region(position, self.state['bassMode'])

    def __store_bass_position_thumb(self, value):
        self.state['bassThumbValue'] = value

    def __set_bass_position_thumb(self):
        self.bassPosition.position_thumb(self.state['bassThumbValue'])

    def __stop_chord_shadow(self):
        reset_notes = []
        for note in self.state['shadowChordNotes']:
            if note != self.state['shadowBassNote']:
                reset_notes.append(note)
        self.keyboard.reset(reset_notes)
        # self.state['shadowChordNotes'] = []

    def __stop_bass_shadow(self):
        note_in_playing_chord = self.state['playingChordNotes'].count(
            self.state['shadowBassNote']) != 0
        note_in_shadow_chord = self.state['shadowChordNotes'].count(
            self.state['shadowBassNote']) != 0
        if (not note_in_playing_chord) and (not note_in_shadow_chord)  \
                and self.state['shadowBassNote'] is not None:
            self.keyboard.reset([self.state['shadowBassNote']])
        # self.state['shadowBassNote'] = None

    def __set_chord(self, chord, root):
        self.state['chordType'] = {'notes': chord, 'root': root}
        self.keyboard.set_chord(chord, root)
        self.chordDisplay.set_chord(chord, root)

    def __play_chord(self, notes):
        self.__stop_chord_shadow()
        self.keyboard.play(notes)
        self.state['playingChordNotes'] = notes
        self.chordDisplay.play_chord()

    def __play_bass(self, note):
        self.__stop_bass_shadow()
        self.keyboard.play([note])
        self.chordDisplay.play_bass(note)
        self.state['playingBassNote'] = note

    def __stop_chord(self, notes):
        self.state['shadowChordNotes'] = notes
        self.keyboard.set_shadow(notes)
        self.state['playingChordNotes'] = []
        self.chordDisplay.set_chord_shadow()

    def __stop_bass(self, note):
        if self.state['playingChordNotes'].count(note) == 0:
            self.keyboard.set_shadow([note])
        self.chordDisplay.set_bass_shadow(note)
        self.state['shadowBassNote'] = note
        self.state['playingBassNote'] = None

    def __set_chord_shadow(self, notes):
        self.keyboard.reset(self.state['shadowChordNotes'])
        self.state['shadowChordNotes'] = notes
        self.keyboard.set_shadow(notes)
        self.chordDisplay.set_chord_shadow()

    def __set_bass_shadow(self, note):
        self.__stop_bass_shadow()
        self.state['shadowBassNote'] = note
        note_in_playing_chord = self.state['playingChordNotes'].count(note) != 0
        if not note_in_playing_chord:
            self.keyboard.set_shadow([note])
        self.chordDisplay.set_bass_shadow(note)

    def __set_modulation(self, new_scale, side):
        self.state['modulationSide'] = side
        self.chordDisplay.set_modulation(new_scale, side)

    def __set_hold(self, hold):
        self.textDisplay.set_hold(hold)

    def __set_inversion_lock(self, inversion_lock):
        self.textDisplay.set_inversion_lock(inversion_lock)

    def __set_octave(self, octave):
        self.textDisplay.set_octave(octave)

    def __set_voice_count(self, voice_count):
        self.textDisplay.set_voices(voice_count)
