from abc import ABC, abstractmethod
from typing import Callable

from models.appParameter import AppParameter, AppParameterType
from models.command import Command
from models.commandType import CommandType
from musicEngine.chordEngine.chordEngineMessage import ChordEngineMessage, ChordMessageType, ChordPlayer
from musicEngine.chordEngine.modules.chordOctave import ChordOctave
from musicEngine.chordEngine.modules.hold import Hold
from musicEngine.chordEngine.modules.inversion.bassPosition import BassPosition
from musicEngine.chordEngine.modules.inversion.chordInversion import ChordInversion
from musicEngine.chordEngine.modules.key import Key
from musicEngine.chordEngine.modules.scale import Scale
from musicEngine.chordEngine.modules.spread import Spread
from musicEngine.chordEngine.modules.voiceCount import VoiceCount
from musicEngine.chordEngine.state.chordsState import ChordButton
from redux import store
from redux import utils as redux_utils
from redux.actions import musicEngine as actions

from .chordEngineState import state


class ChordEngine(ABC):

    type: AppParameterType

    scale: Scale
    inversion: ChordInversion
    bass_position: BassPosition
    key: Key
    spread: Spread
    chord_octave: ChordOctave
    voice_count: VoiceCount
    hold: Hold

    callbacks: list[Callable]

    def __init__(self, type: AppParameterType):

        self.type = type

        self.scale = Scale()
        self.inversion = ChordInversion(type, self.update_chord)
        self.bass_position = BassPosition(type, self.update_bass)
        self.key = Key(type, self.update_chord_type)
        self.spread = Spread(type, self.update_chord)
        self.chord_octave = ChordOctave(type, self.update_chord)
        self.voice_count = VoiceCount(type, self.update_chord)
        self.hold = Hold(type, self.stop_chord_and_bass)

        self.callbacks = []

        redux_utils.add_app_parameters(self.get_parameters())

    @abstractmethod
    def get_chord_note_classes(self):
        pass

    @abstractmethod
    def get_chord_notes(self, button):
        pass

    @abstractmethod
    def get_bass_note(self):
        pass

    def subscribe(self, callback):
        self.callbacks.append(callback)

    def send_message(self, message):
        for callback in self.callbacks:
            callback(message)

    def send_notes_on(self, notes: list[int], player: ChordPlayer):
        message = ChordEngineMessage(
            type=ChordMessageType.ON,
            notes=notes,
            player=player
        )
        self.send_message(message)

    def send_notes_off(self, notes: list[int], player: ChordPlayer):
        message = ChordEngineMessage(
            type=ChordMessageType.OFF,
            notes=notes,
            player=player
        )
        self.send_message(message)

    def chord_button_on(self, button):
        already_active = (len(state.chord.button_queue) > 0
                         and state.chord.button_queue[-1] == button)
        if state.chord.button_queue.count(button) > 0:
            state.chord.button_queue.remove(button)
        state.chord.button_queue.append(button)
        if not already_active:
            self.update_chord_from_control_state()

    def chord_button_off(self, button):
        if len(state.chord.button_queue) == 0:
            return
        last_button = state.chord.button_queue[-1]
        if state.chord.button_queue.count(button) > 0:
            state.chord.button_queue.remove(button)
        if button == last_button:
            self.update_chord_from_control_state()

    def update_chord_from_control_state(self):
        if len(state.chord.button_queue) == 0:
            self.stop_chord()
        else:
            button = state.chord.button_queue[-1]
            self.play_chord(button)

    def play_chord(self, button=None):
        if button is not None:
            state.chord.active_button = button
        self.set_chord_type()
        self.stop_chord(force=True)
        notes = self.get_chord_notes(button)
        self.send_notes_on(notes, player=ChordPlayer.CHORD)
        self.update_bass(from_chord=True)
        state.chord.playing_notes = notes
        state.chord.is_playing = True

    def play_bass(self):
        self.stop_bass(button_up=False)
        bass_note = self.get_bass_note()
        self.send_notes_on([bass_note], player=ChordPlayer.BASS)
        store.dispatch(actions.play_bass(bass_note))
        state.bass.playing_note = bass_note
        state.bass.is_playing = True

    def stop_chord_and_bass(self):
        self.stop_chord()
        self.stop_bass(button_up=False)

    def stop_chord(self, force=False):
        if ((not state.hold and state.chord.is_playing) or force) and state.chord.playing_notes:
            playing_notes = state.chord.playing_notes
            self.send_notes_off(playing_notes, player=ChordPlayer.CHORD)
            store.dispatch(actions.stop_chord())
            state.chord.playing_notes = []
            state.chord.is_playing = False

    def stop_bass(self, button_up=True):
        if not (button_up and state.hold) and state.bass.is_playing:
            playing_bass = state.bass.playing_note
            self.send_notes_off([playing_bass], player=ChordPlayer.BASS)
            store.dispatch(actions.stop_bass())
            state.bass.playing_note = None
            state.bass.is_playing = False

    def update_chord_type(self):
        self.set_chord_type()
        self.update_chord()
        self.update_bass()

    def set_chord_type(self):
        chord_note_classes, root_class = self.get_chord_note_classes()
        if chord_note_classes != state.chord.note_classes or root_class != state.chord.root_class:
            state.chord.note_classes, state.chord.root_class = chord_note_classes, root_class
            store.dispatch(actions.change_chord_type({'chord': chord_note_classes, 'root': root_class}))

    def update_chord(self):
        if (state.chord.is_playing):
            self.play_chord(state.chord.active_button)
        else:
            notes = self.get_chord_notes(state.chord.active_button)
            store.dispatch(actions.change_chord_shadow(notes))

    def update_bass(self, from_chord=False):
        if (state.bass.is_playing):
            if from_chord:
                bass_note = self.get_bass_note()
                if state.bass.playing_note != bass_note:
                    self.play_bass()
            else:
                self.play_bass()
        else:
            note = self.get_bass_note()
            store.dispatch(actions.change_bass_shadow(note))

    def get_parameters(self):
        key_prefix = "EXTERNAL_" if self.type == AppParameterType.EXTERNAL_CHORD_ENGINE else "INTERNAL_"
        return[
            AppParameter(
                valid_command_types = [CommandType.ON_OFF],
                command_mappings = {
                    Command.ON: lambda: self.chord_button_on(ChordButton.SOUTH),
                    Command.OFF: lambda: self.chord_button_off(ChordButton.SOUTH)
                },
                key = f"{key_prefix}SOUTH_CHORD",
                label = "South Chord",
                label_abreviation="S",
                type = self.type
            ),
            AppParameter(
                valid_command_types = [CommandType.ON_OFF],
                command_mappings = {
                    Command.ON: lambda: self.chord_button_on(ChordButton.WEST),
                    Command.OFF: lambda: self.chord_button_off(ChordButton.WEST)
                },
                key = f"{key_prefix}WEST_CHORD",
                label = "West Chord",
                label_abreviation="W",
                type = self.type
            ),
            AppParameter(
                valid_command_types = [CommandType.ON_OFF],
                command_mappings = {
                    Command.ON: lambda: self.chord_button_on(ChordButton.NORTH),
                    Command.OFF: lambda: self.chord_button_off(ChordButton.NORTH)
                },
                key = f"{key_prefix}NORTH_CHORD",
                label = "North Chord",
                label_abreviation="N",
                type = self.type
            ),
            AppParameter(
                valid_command_types = [CommandType.ON_OFF],
                command_mappings = {
                    Command.ON: lambda: self.chord_button_on(ChordButton.EAST),
                    Command.OFF: lambda: self.chord_button_off(ChordButton.EAST)
                },
                key = f"{key_prefix}EAST_CHORD",
                label = "East Chord",
                label_abreviation="E",
                type = self.type
            ),
            AppParameter(
                valid_command_types = [CommandType.ON_OFF],
                command_mappings = {
                    Command.ON: self.play_bass,
                    Command.OFF: self.stop_bass
                },
                key = f"{key_prefix}BASS",
                label = "Bass",
                label_abreviation="B",
                type = self.type
            )
        ]
