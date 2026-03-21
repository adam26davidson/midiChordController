import asyncio
import copy
import math
from typing import Optional, TypedDict

from numpy import random
from pyrsistent import thaw
from rtmidi import MidiIn, MidiOut  # type: ignore[attr-defined]
from rtmidi.midiconstants import *  # noqa: F403

from constants import *  # noqa: F403
from music_engine.midi.midi_input_message import MidiInputMessage, MidiInputMessageType
from redux import store
from redux.actions import music_engine as actions


class MidiState(TypedDict):
    midiOutputConnected: bool
    midiOutputControllerNames: list[str]
    midiInputConnected: bool
    midiInputControllerNames: list[str]
    midiInputNotesOn: dict[int, list[dict[str, object]]]
    mergedMidiInputNotesOn: list[int]
    velocity: int
    velocityMode: str
    velocityDeviation: int
    playingChordNotes: list[int]
    playingBassNote: Optional[int]
    distributeChannels: bool
    occupiedChannels: dict[int, bool]
    distChordChannels: dict[int, int]
    chordChannel: int
    bassChannel: int
    aftertouchMode: str
    afterTouch: int
    lastSentAfterTouch: int
    CCValues: dict[int, int]
    lastSentCCValues: dict[int, Optional[int]]


class Midi:
    def __init__(self):
        self.utility_midi_out = MidiOut()
        self.utility_midi_in = MidiIn()
        self.midi_out_instances = []
        self.midi_in_instances = []
        self.subscriber_callbacks = []

        self.midi_input_message_queue: list[MidiInputMessage] = []

        self.state: MidiState = {
            'midiOutputConnected': False,
            'midiOutputControllerNames': [],
            'midiInputConnected': False,
            'midiInputControllerNames': [],
            'midiInputNotesOn': {},
            'mergedMidiInputNotesOn': [],

            'velocity': 100, # constant velocity or center of random distribution
            'velocityMode': 'random', # 'constant' or 'random'
            'velocityDeviation': 15, # 'standard deviation for random velocity'

            'playingChordNotes': [],
            'playingBassNote': None,

            'distributeChannels': False,
            'occupiedChannels': {},
            'distChordChannels': {},
            'chordChannel': 0,
            'bassChannel': 0,

            'aftertouchMode': 'channel', # 'channel' or 'poly'. default is to use channel aftertouch
            'afterTouch': 0,
            'lastSentAfterTouch': 0,
            'CCValues': {},
            'lastSentCCValues': {},
        }

        for channel in range(16):
            if self.state['bassChannel'] == channel:
                self.state['occupiedChannels'][channel] = True
            else:
                self.state['occupiedChannels'][channel] = False


        for note in range(128):
            self.state['distChordChannels'][note] = 0

        store.subscribe(self.__handle_store_update)

    def start(self):
        self.available_output_ports = self.utility_midi_out.get_ports()
        self.available_input_ports = self.utility_midi_in.get_ports()
        print(f"output ports: {self.available_output_ports}")
        print(f"input ports: {self.available_input_ports}")

        for i in range(1, len(self.available_input_ports)):
            port_name = self.available_input_ports[i]
            midi_in = MidiIn()
            current_ports = midi_in.get_ports()
            try:
                port_index = current_ports.index(port_name)
            except ValueError:
                continue
            midi_in.open_port(port_index)
            self.midi_in_instances.append(midi_in)
            midi_in.set_callback(self.handle_midi_in, port_name)
            self.state['midiInputControllerNames'].append(port_name)

        for i in range(1, len(self.available_output_ports)):
            port_name = self.available_output_ports[i]
            midi_out = MidiOut()
            current_ports = midi_out.get_ports()
            try:
                port_index = current_ports.index(port_name)
            except ValueError:
                continue
            midi_out.open_port(port_index)
            self.midi_out_instances.append(midi_out)
            self.state['midiOutputControllerNames'].append(port_name)

        _task = asyncio.ensure_future(self.__output_loop())

    def subscribe(self, callback):
        self.subscriber_callbacks.append(callback)

    def handle_midi_in(self, message, data):
        midi_message = message[0]
        status_byte = midi_message[0]
        midi_command = status_byte & 0xF0 # get the higher nibble
        channel = status_byte & 0x0F     # get the lower nibble

        if midi_command == NOTE_ON and midi_message[2] > 0:
            note = midi_message[1]
            self.add_midi_input_note_on(note, channel, data)

        elif midi_command == NOTE_OFF or (midi_command == NOTE_ON and midi_message[2] == 0):
            note = midi_message[1]
            self.remove_midi_input_note_on(note, channel, data)

    def add_midi_input_note_on(self, note, channel, controller):
        if note not in self.state['midiInputNotesOn']:
            self.state['midiInputNotesOn'][note] = []
        note_found = False
        for note_obj in self.state['midiInputNotesOn'][note]:
            if note_obj['channel'] == channel and note_obj['controller'] == controller:
                note_found = True
                break
        if not note_found:
            self.state['midiInputNotesOn'][note].append({
                'channel': channel,
                'controller': controller
            })
        if note not in self.state['mergedMidiInputNotesOn']:
            self.state['mergedMidiInputNotesOn'].append(note)
            self.send_message(
                MidiInputMessage(
                    MidiInputMessageType.NOTE_ON,
                    note
                    ))

    def remove_midi_input_note_on(self, note, channel, controller):
        note_is_not_played_anywhere = False
        if note in self.state['midiInputNotesOn']:
            for note_obj in self.state['midiInputNotesOn'][note]:
                if note_obj['channel'] == channel and note_obj['controller'] == controller:
                    self.state['midiInputNotesOn'][note].remove(note_obj)
                    if len(self.state['midiInputNotesOn'][note]) == 0:
                        note_is_not_played_anywhere = True
                    break
        if note in self.state['mergedMidiInputNotesOn'] and note_is_not_played_anywhere:
            self.state['mergedMidiInputNotesOn'].remove(note)
            self.send_message(
                MidiInputMessage(
                    MidiInputMessageType.NOTE_OFF,
                    note
                    ))

    def send_message(self, message):
        for callback in self.subscriber_callbacks:
            callback(message)

    def handle_message(self, message):
        # if not self.state['midiOutputConnected']:
        # return None

        note, player, type = message['note'], message['player'], message['type']
        if type == 'on':
            self.__note_on(note, player)
        elif type == 'off':
            self.__note_off(note, player)

    def set_after_touch(self, value):
        self.state['afterTouch'] = min(math.floor(((value+1) / 2)*128), 127)

    def get_cc_setter(self, cc):
        self.state['lastSentCCValues'][cc] = None
        def set_cc_value(value):
            self.state['CCValues'][cc] = min(math.floor(((value+1) / 2)*128), 127)
        return set_cc_value

    def __handle_store_update(self):
        state = store.get_state()
        me_state = thaw(state['musicEngine'])
        if (me_state['bassChannel'] != self.state['bassChannel']):
            self.__set_bass_channel(me_state['bassChannel'])
        if (me_state['chordChannel'] != self.state['chordChannel']):
            self.__set_chord_channel(me_state['chordChannel'])
        if (me_state['distributeChannels'] != self.state['distributeChannels']):
            self.__set_distribute_channels(me_state['distributeChannels'])
        if (me_state['velocity'] != self.state['velocity']):
            self.__set_velocity(me_state['velocity'])
        if (me_state['velocityMode'] != self.state['velocityMode']):
            self.__set_velocity_mode(me_state['velocityMode'])
        if (me_state['velocityDeviation'] != self.state['velocityDeviation']):
            self.__set_velocity_deviation(me_state['velocityDeviation'])
        if (me_state['aftertouchMode'] != self.state['aftertouchMode']):
            self.__set_aftertouch_mode(me_state['aftertouchMode'])

    async def __output_loop(self):
        while True:
            ports = self.utility_midi_out.get_ports()

            if self.available_output_ports == ports:
                self.__send_after_touch()
                self.__send_cc_values()
            else:
                self.available_output_ports = ports
                self.__reconnect()
            await asyncio.sleep(MIDI_OUTPUT_STEP)

    def __reconnect(self):
        print("RECONNECTING TO MIDI OUTPUTS")
        for midi_out in self.midi_out_instances:
            if midi_out.is_port_open():
                midi_out.close_port()
            midi_out.delete()

        self.available_output_ports = self.utility_midi_out.get_ports()
        print(self.available_output_ports)

        self.midi_out_instances = []
        self.state['midiOutputControllerNames'] = []
        for i in range(1, len(self.available_output_ports)):
            port_name = self.available_output_ports[i]
            if port_name.count('Midi Through') > 0 or port_name.count('RtMidi') > 0:
                continue
            midi_out = MidiOut()
            current_ports = midi_out.get_ports()
            try:
                port_index = current_ports.index(port_name)
            except ValueError:
                continue
            midi_out.open_port(port_index)
            self.midi_out_instances.append(midi_out)
            self.state['midiOutputControllerNames'].append(port_name)

    def __set_bass_channel(self, channel):
        if (channel < 0 or channel > 15):
            store.dispatch(actions.change_bass_channel(self.state['bassChannel']))
        else:
            # if chord is playing and distribute channels is on, stop chord
            chord_notes = copy.deepcopy(self.state['playingChordNotes'])
            if self.state['distributeChannels'] and len(chord_notes) > 0:
                for note in chord_notes:
                    self.__note_off(note, 'chord')

            # open up old bass channel
            self.state['occupiedChannels'][self.state['bassChannel']] = False

            #update bass to play on new channel, set state bass channel
            if self.state['playingBassNote']:
                note = self.state['playingBassNote']
                self.__note_off(note, 'bass')
                self.state['bassChannel'] = channel
                self.state['occupiedChannels'][channel] = True
                self.__note_on(note, 'bass')
            else:
                self.state['bassChannel'] = channel

            # replay re-distributed chord
            if self.state['distributeChannels'] and len(chord_notes) > 0:
                for note in chord_notes:
                    self.__note_on(note, 'chord')

    def __set_chord_channel(self, channel):
        if (channel < 0 or channel > 15):
            store.dispatch(actions.change_chord_channel(self.state['chordChannel']))
        else:
            if len(self.state['playingChordNotes']) > 0:
                notes = copy.deepcopy(self.state['playingChordNotes'])
                for note in notes:
                    self.__note_off(note, 'chord')
                self.state['chordChannel'] = channel
                for note in notes:
                    self.__note_on(note, 'chord')
            else:
                self.state['chordChannel'] = channel

    def __set_distribute_channels(self, distribute):
        if len(self.state['playingChordNotes']) > 0 or self.state['playingBassNote']:
            chord_notes = copy.deepcopy(self.state['playingChordNotes'])
            for note in chord_notes:
                self.__note_off(note, 'chord')
            self.state['distributeChannels'] = distribute
            for note in chord_notes:
                self.__note_on(note, 'chord')
        else:
            self.state['distributeChannels'] = distribute

    def __set_velocity(self, velocity):
        self.state['velocity'] = velocity

    def __set_velocity_mode(self, mode):
        self.state['velocityMode'] = mode

    def __set_velocity_deviation(self, deviation):
        self.state['velocityDeviation'] = deviation

    def __set_aftertouch_mode(self, aftertouch_mode):
        self.state['aftertouchMode'] = aftertouch_mode

    def __send_midi_message(self, message):
        # self.midiOut.send_message(message)
        for midi_out in self.midi_out_instances:
            midi_out.send_message(message)

    def __note_off(self, note, player):
        note_channel = self.__get_note_channel(note, player, 'off')
        #print(f'OFF -- note: {note}, channel: {note_channel}, player: {player}')
        channel_command = self.__combine_command_and_channel(NOTE_OFF, note_channel)
        self.__send_midi_message([channel_command, note, 0])
        self.__store_note_off(note, player)

    def __note_on(self, note, player):
        velocity = self.__get_velocity()
        note_channel = self.__get_note_channel(note, player, 'on')
        #print(f'ON -- note: {note}, channel: {note_channel}, player: {player}')
        channel_command = self.__combine_command_and_channel(NOTE_ON, note_channel)
        self.__send_midi_message([channel_command, note, velocity])
        self.__store_note_on(note, player, note_channel)
        self.__send_after_touch(force=True)
        if player == 'chord':
            store.dispatch(actions.play_chord(self.state['playingChordNotes']))

    def __store_note_on(self, note: int, player: str, channel: Optional[int] = None) -> None:
        if player == 'chord':
            if note not in self.state['playingChordNotes']:
                self.state['playingChordNotes'].append(note)
        elif player == 'bass':
            self.state['playingBassNote'] = note
        if self.state['distributeChannels'] and player == 'chord' and channel is not None:
            self.state['distChordChannels'][note] = channel

    def __store_note_off(self, note, player):
        if self.state['distributeChannels'] and player == 'chord':
            self.__open_channel(note, player)
        if player == 'chord':
            if note in self.state['playingChordNotes']:
                self.state['playingChordNotes'].remove(note)
        else:
            self.state['playingBassNote'] = None

        # this is here just in case a channel gets stuck on occupied
        if self.state['distributeChannels'] \
            and len(self.state['playingChordNotes']) == 0 \
            and self.state['playingBassNote'] is None:
            for channel in range(16):
                if channel != self.state['bassChannel']:
                    self.state['occupiedChannels'][channel] = False

    def __get_note_channel(self, note, player, type):
        if player == 'chord':
            if self.state['distributeChannels']:
                if type == 'on':
                    return self.__distribute_channel()
                return self.state['distChordChannels'][note]
            return self.state['chordChannel']
        if player == 'bass':
            return self.state['bassChannel']
        return None

    def __send_channel_after_touch(self, force=False):
        if not force and (self.state['afterTouch'] == self.state['lastSentAfterTouch']):
            return

        aftertouch_value = self.state['afterTouch']
        if self.state['distributeChannels']:
            channels = filter(
                lambda x: self.state['occupiedChannels'][x],
                self.state['occupiedChannels'].keys())
            for channel in channels:
                channel_command = self.__combine_command_and_channel(CHANNEL_PRESSURE, channel)
                self.__send_midi_message([channel_command, aftertouch_value])
        else:
            channel = self.state['chordChannel']
            channel_command = self.__combine_command_and_channel(CHANNEL_PRESSURE, channel)
            self.__send_midi_message([channel_command, aftertouch_value])

        if self.state['playingBassNote']:
            channel = self.state['bassChannel']
            channel_command = self.__combine_command_and_channel(CHANNEL_PRESSURE, channel)
            self.__send_midi_message([channel_command, aftertouch_value])

        self.state['lastSentAfterTouch'] = self.state['afterTouch']

    def __send_polyphonic_aftertouch(self, force=False):
        if not force and (self.state['afterTouch'] == self.state['lastSentAfterTouch']):
            return

        # send poly aftertouch for each chord note
        for note in self.state['playingChordNotes']:
            channel = self.state['chordChannel']
            if self.state['distributeChannels']:
                channel = self.state['distChordChannels'][note]
            channel_command = self.__combine_command_and_channel(POLY_AFTERTOUCH, channel)
            self.__send_midi_message([channel_command, note, self.state['afterTouch']])

        #send poly aftertouch for bass note
        if self.state['playingBassNote']:
            bass_note = self.state['playingBassNote']
            channel = self.state['bassChannel']
            channel_command = self.__combine_command_and_channel(POLY_AFTERTOUCH, channel)
            self.__send_midi_message([channel_command, bass_note, self.state['afterTouch']])

        self.state['lastSentAfterTouch'] = self.state['afterTouch']

    def __send_after_touch(self, force=False):
        if self.state['aftertouchMode']=='poly':
            self.__send_polyphonic_aftertouch(force)
        else:
            self.__send_channel_after_touch(force)

    def __send_cc_values(self):
        for cc, val in self.state['CCValues'].items():
            if val != self.state['lastSentCCValues'][cc]:
                for channel in range(16):
                    channel_command = self.__combine_command_and_channel(CONTROL_CHANGE, channel)
                    self.__send_midi_message([channel_command, cc, val])
                self.state['lastSentCCValues'][cc] = val

    def __combine_command_and_channel(self, command, channel):
        return ((command & 0xf0) | (channel & 0xf))

    def __distribute_channel(self):
        for channel in range(16):
            #print(f"{channel}: {self.state['occupiedChannels'][channel]}")
            if not self.state['occupiedChannels'][channel]:
                self.state['occupiedChannels'][channel] = True
                return channel
        return 0

    def __open_channel(self, note, player):
        if player == 'chord':
            channel = self.state['distChordChannels'][note]
            self.state['occupiedChannels'][channel] = False

    def __get_random_velocity(self):
        value = random.normal(
            loc = self.state['velocity'],
            scale = self.state['velocityDeviation']
        )
        return int(max(min(value, 127), 0))

    def __get_velocity(self):
        if self.state['velocityMode'] == 'constant':
            return self.state['velocity']
        if self.state['velocityMode'] == 'random':
            return self.__get_random_velocity()
        return None
