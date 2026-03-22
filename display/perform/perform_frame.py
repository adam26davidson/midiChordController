from __future__ import annotations

import logging
import tkinter as tk
from typing import TypedDict

from models.app_parameter import AppParameter, AppParameterType
from models.command import Command
from models.command_type import CommandType
from redux import get_controller_manager_state, get_music_engine_state, store
from redux import utils as redux_utils

from ..chord_display import ChordDisplay
from .control_display.control_display import ControlDisplay
from .inversion import Inversion
from .keyboard import Keyboard
from .setting_display import SettingDisplay
from .spread import Spread
from .text_display import TextDisplay

logger = logging.getLogger(__name__)


class ChordTypeState(TypedDict):
    notes: list[int]
    root: int


class PerformFrameState(TypedDict):
    settingIndex: int
    settingName: str
    settingLoading: bool
    controllerName: str
    chordType: ChordTypeState
    shadowChordNotes: list[int]
    playingChordNotes: list[int]
    shadowBassNote: int
    playingBassNote: int | None
    chordOctave: int
    voiceCount: int
    inversionThumbValue: float
    inversionMode: str
    inversionLock: bool
    hold: bool
    bassThumbValue: float
    bassMode: str
    bassPosition: int
    bassRange: int
    inversion: int
    inversionRange: int
    key: int
    scale: list[int]
    alternate: str
    modulationSide: str


class PerformFrame(tk.Frame):

    height: int = 480
    width: int = 800

    def __init__(self, container: tk.Misc) -> None:
        super().__init__(container, highlightthickness=0, relief="flat", bg="#000000")

        self.state: PerformFrameState = {
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
        self.bass_position = Inversion(master=self)
        self.chordTextFrame = tk.Frame(self, bg="#000000")
        self.chordTextFrame.pack(side="right", padx=(0, 30))
        self.chord_display = ChordDisplay(master=self.chordTextFrame)
        self.text_display = TextDisplay(master=self.chordTextFrame)
        self.setting_display = SettingDisplay(master=self)
        self.control_display = ControlDisplay(master=self)

        self.grid(row=0, column=0, sticky='nsew')

        redux_utils.add_app_parameters(self.get_parameters())

        self._dirty: bool = False
        store.subscribe(self.__handle_store_update)

    def __handle_store_update(self) -> None:
        self._dirty = True

    def check_state(self) -> None:
        self.spread.check_state()
        self.setting_display.check_state()
        self.control_display.check_state()

        if not self._dirty:
            return
        self._dirty = False

        me_state = get_music_engine_state()
        c_state = get_controller_manager_state()

        # 1. Scale context: key, scale, modulation — must resolve before chord visuals
        if me_state['key'] != self.state['key']:
            self.__set_key(me_state['key'])
        if me_state['modulation']['side'] != self.state['modulationSide']:
            self.__set_modulation(me_state['modulation']['scale'], me_state['modulation']['side'])
        if me_state['scale'] != self.state['scale']:
            self.__set_scale(me_state['scale'])

        # 2. Chord definition — must resolve before playing/shadow notes
        if me_state['chordType']['chord'] != self.state['chordType']['notes'] or \
                me_state['chordType']['root'] != self.state['chordType']['root']:
            self.__set_chord(me_state['chordType']['chord'], me_state['chordType']['root'])

        # 3. Playing/shadow state — uses current scale, chord type, and positions
        if me_state['chordShadow'] != self.state['shadowChordNotes']:
            self.__set_chord_shadow(me_state['chordShadow'])
        if me_state['chordNotes'] != self.state['playingChordNotes']:
            logger.debug("chordNotes changed: store=%s local=%s", me_state['chordNotes'], self.state['playingChordNotes'])
            if len(me_state['chordNotes']) > 0:
                self.__play_chord(me_state['chordNotes'])
            else:
                self.__stop_chord(self.state['playingChordNotes'])
        if me_state['inversion'] != self.state['inversion']:
            logger.debug("inversion changed: store=%s local=%s", me_state['inversion'], self.state['inversion'])
        if me_state['bassShadow'] != self.state['shadowBassNote']:
            self.__set_bass_shadow(me_state['bassShadow'])
        if me_state['bassNote'] != self.state['playingBassNote']:
            if me_state['bassNote'] is not None:
                self.__play_bass(me_state['bassNote'])
            else:
                self.__stop_bass(self.state['playingBassNote'])

        # 4. Inversion/position ranges
        if me_state['inversion'] != self.state['inversion']:
            self.__set_inversion(me_state['inversion'])
        if me_state['bassPosition'] != self.state['bassPosition']:
            self.__set_bass_position(me_state['bassPosition'])
        if me_state['inversionRange'] != self.state['inversionRange']:
            self.__set_inversion_range(me_state['inversionRange'], me_state['inversion'])
        if me_state['bassRange'] != self.state['bassRange']:
            self.__set_bass_range(me_state['bassRange'], me_state['bassPosition'])
        if me_state['setting'] != self.state['settingIndex'] and len(me_state['settingsList']) > 0:
            self.state['settingName'] = me_state['settingsList'][me_state['setting']]
            self.state['settingIndex'] = me_state['setting']
            self.__set_setting(self.state['settingName'])
            logger.debug("setting name: %s", self.state['settingName'])
        if me_state['settingLoading'] != self.state['settingLoading']:
            if me_state['settingLoading']:
                self.__set_setting_loading()
            else:
                self.state['settingLoading'] = False
                self.__set_setting(self.state['settingName'])
        if me_state['hold'] != self.state['hold']:
            self.state['hold'] = me_state['hold']
            self.__set_hold(self.state['hold'])
        if me_state['inversionLock'] != self.state['inversionLock']:
            self.state['inversionLock'] = me_state['inversionLock']
            self.__set_inversion_lock(self.state['inversionLock'])
        if me_state['chordOctave'] != self.state['chordOctave']:
            self.state['chordOctave'] = me_state['chordOctave']
            self.__set_octave(self.state['chordOctave'])
        if me_state['voiceCount'] != self.state['voiceCount']:
            self.state['voiceCount'] = me_state['voiceCount']
            self.__set_voice_count(self.state['voiceCount'])

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

    def get_parameters(self) -> list[AppParameter]:
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

    def update_frame(self) -> None:
        if not self.state['inversionLock']:
            self.__set_inversion_thumb()
        if self.state['bassMode'] == 'continuous':
            self.__set_bass_position_thumb()
        self.chord_display.run_animation_step()

    def __set_controller(self, text: str) -> None:
        self.text_display.set_controller(text)

    def __set_setting_loading(self) -> None:
        self.state['settingLoading'] = True
        self.setting_display.set_setting('Loading...')

    def __set_setting(self, text: str) -> None:
        if not self.state['settingLoading']:
            self.setting_display.set_setting(text)

    def __set_key(self, key: int) -> None:
        self.state['key'] = key
        self.chord_display.set_key(key)

    def __set_scale(self, scale: list[int]) -> None:
        self.state['scale'] = scale
        self.chord_display.set_scale(scale)

    def __set_inversion_range(self, range: int, inversion: int) -> None:
        self.state['inversionRange'] = range
        self.state['inversion'] = inversion
        self.inversion.set_max(range, inversion)

    def __set_inversion(self, inversion: int) -> None:
        self.state['inversion'] = inversion
        self.inversion.set_active_region(inversion, self.state['inversionMode'])

    def __store_inversion_thumb(self, value: float) -> None:
        self.state['inversionThumbValue'] = value

    def __set_inversion_thumb(self) -> None:
        self.inversion.position_thumb(self.state['inversionThumbValue'])

    def __set_bass_range(self, range: int, position: int) -> None:
        self.state['bassRange'] = range
        self.state['bassPosition'] = position
        self.bass_position.set_max(range, position)

    def __set_bass_position(self, position: int) -> None:
        self.state['bassPosition'] = position
        self.bass_position.set_active_region(position, self.state['bassMode'])

    def __store_bass_position_thumb(self, value: float) -> None:
        self.state['bassThumbValue'] = value

    def __set_bass_position_thumb(self) -> None:
        self.bass_position.position_thumb(self.state['bassThumbValue'])

    def __stop_chord_shadow(self) -> None:
        reset_notes: list[int] = []
        for note in self.state['shadowChordNotes']:
            if note != self.state['shadowBassNote']:
                reset_notes.append(note)
        self.keyboard.reset(reset_notes)

    def __stop_bass_shadow(self) -> None:
        note_in_playing_chord = self.state['playingChordNotes'].count(
            self.state['shadowBassNote']) != 0
        note_in_shadow_chord = self.state['shadowChordNotes'].count(
            self.state['shadowBassNote']) != 0
        if (not note_in_playing_chord) and (not note_in_shadow_chord)  \
                and self.state['shadowBassNote'] is not None:
            self.keyboard.reset([self.state['shadowBassNote']])

    def __set_chord(self, chord: list[int], root: int) -> None:
        self.state['chordType'] = {'notes': chord, 'root': root}
        self.keyboard.set_chord(chord, root)
        self.chord_display.set_chord(chord, root)
        if self.state['playingChordNotes']:
            self.keyboard.play(self.state['playingChordNotes'])

    def __play_chord(self, notes: list[int]) -> None:
        self.__stop_chord_shadow()
        old_notes = self.state['playingChordNotes']
        if old_notes:
            removed = [n for n in old_notes if n not in notes]
            if removed:
                self.keyboard.reset(removed)
        self.keyboard.play(notes)
        self.state['playingChordNotes'] = notes
        self.chord_display.play_chord()

    def __play_bass(self, note: int) -> None:
        self.__stop_bass_shadow()
        old_note = self.state['playingBassNote']
        if old_note and old_note != note:
            note_in_chord = old_note in self.state['playingChordNotes']
            if not note_in_chord:
                self.keyboard.reset([old_note])
        self.keyboard.play([note])
        self.chord_display.play_bass(note)
        self.state['playingBassNote'] = note

    def __stop_chord(self, notes: list[int]) -> None:
        self.state['shadowChordNotes'] = notes
        self.keyboard.set_shadow(notes)
        self.state['playingChordNotes'] = []
        self.chord_display.set_chord_shadow()

    def __stop_bass(self, note: int | None) -> None:
        if note is not None:
            if self.state['playingChordNotes'].count(note) == 0:
                self.keyboard.set_shadow([note])
            self.chord_display.set_bass_shadow(note)
            self.state['shadowBassNote'] = note
        self.state['playingBassNote'] = None

    def __set_chord_shadow(self, notes: list[int]) -> None:
        self.keyboard.reset(self.state['shadowChordNotes'])
        self.state['shadowChordNotes'] = notes
        self.keyboard.set_shadow(notes)
        self.chord_display.set_chord_shadow()

    def __set_bass_shadow(self, note: int) -> None:
        self.__stop_bass_shadow()
        self.state['shadowBassNote'] = note
        note_in_playing_chord = self.state['playingChordNotes'].count(note) != 0
        if not note_in_playing_chord:
            self.keyboard.set_shadow([note])
        self.chord_display.set_bass_shadow(note)

    def __set_modulation(self, new_scale: list[int], side: str) -> None:
        self.state['modulationSide'] = side
        self.chord_display.set_modulation(new_scale, side)

    def __set_hold(self, hold: bool) -> None:
        self.text_display.set_hold(hold)

    def __set_inversion_lock(self, inversion_lock: bool) -> None:
        self.text_display.set_inversion_lock(inversion_lock)

    def __set_octave(self, octave: int) -> None:
        self.text_display.set_octave(octave)

    def __set_voice_count(self, voice_count: int) -> None:
        self.text_display.set_voices(voice_count)
