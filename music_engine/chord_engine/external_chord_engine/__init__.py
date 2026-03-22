from __future__ import annotations

import asyncio
import threading

from constants import MIDI_INPUT_STEP
from models.app_parameter import AppParameterType
from music_engine.chord_engine.chord_engine import ChordEngine
from music_engine.chord_engine.external_chord_engine.modules.note_history import NoteHistory
from music_engine.chord_engine.modules.chords import Chord
from music_engine.chord_engine.state.chords_state import ChordButton
from music_engine.midi.midi_input_message import MidiInputMessage, MidiInputMessageType

from ..chord_engine_state import ExternalChordMode, ExternalChordScaleMode, state


class ExternalChordEngine(ChordEngine):

    input_queue: list[MidiInputMessage]
    note_history: NoteHistory

    def __init__(self) -> None:
        super().__init__(AppParameterType.EXTERNAL_CHORD_ENGINE)

        self.note_history = NoteHistory()
        self.input_queue = []
        self.input_queue_lock = threading.Lock()

        self.chords = {
            ChordButton.SOUTH: Chord([0, 3, 7], [0], 0),
            ChordButton.WEST: Chord([0, 3, 7], [0], 0),
            ChordButton.NORTH: Chord([0, 3, 7], [0], 0),
            ChordButton.EAST: Chord([0, 3, 7], [0], 0)
        }

    def get_chord_note_classes(self) -> tuple[list[int], int]:
        chord = self.chords[state.chord.active_button]
        root_type = chord.get_root()
        chord_types = chord.get_note_types()
        return chord_types, root_type

    def get_chord_notes(self, button: ChordButton) -> list[int]:
        chord = self.chords[button]
        chord_notes = chord.get_chord()
        chord_adjusted_octaves = self.chord_octave.apply(chord_notes)
        return chord_adjusted_octaves

    def get_bass_note(self) -> int:
        chord = self.chords[state.chord.active_button]
        return chord.get_bass()

    def start(self) -> None:
        _task = asyncio.ensure_future(self.__input_loop())

    def handle_midi_message(self, message: MidiInputMessage) -> None:
        with self.input_queue_lock:
            self.input_queue.append(message)

    async def __input_loop(self) -> None:
        while True:
            with self.input_queue_lock:
                queue = self.input_queue
                self.input_queue = []
            if len(queue) > 0:
                self.process_queue(queue)
            await asyncio.sleep(MIDI_INPUT_STEP)

    def process_queue(self, queue: list[MidiInputMessage]) -> None:
        last_contiguous_classes = list(state.note_in_history.lastContiguousClasses)
        last_contiguous_classes.sort()
        for message in queue:
            if message.type == MidiInputMessageType.NOTE_ON:
                self.note_history.note_on(message.note)
            elif message.type == MidiInputMessageType.NOTE_OFF:
                self.note_history.note_off(message.note)
        new_contiguous_classes = list(state.note_in_history.lastContiguousClasses)
        new_contiguous_classes.sort()
        if last_contiguous_classes != new_contiguous_classes:
            print("new chord")
            self.determine_chord_and_scale()

    def determine_chord_and_scale(self) -> None:
        if state.chord_mode == ExternalChordMode.MOST_RECENT_NOTE_SET:
            note_classes = state.note_in_history.lastContiguousClasses
            key, scale = self.get_scale_and_key(note_classes)

            self.scale.update(scale)
            self.key.set(key)

            lowest_class = state.note_in_history.lowest_in_contiguous_classes % 12
            root_class = lowest_class
            key_agnostic_root = self.rotate_back(key, [root_class])[0]
            key_agnostic_chord = self.rotate_back(key, note_classes)
            root_index = scale.index(key_agnostic_root)

            chord_indices = [scale.index(note_class) for note_class in key_agnostic_chord]
            chord_indices_from_root = [
                (chord_index + (len(scale) - root_index)) % len(scale)
                for chord_index in chord_indices
            ]
            chord_indices_from_root.sort()

            if len(chord_indices_from_root) > 1:
                no_root_chord_indices_from_root = chord_indices_from_root[1:]
            else:
                no_root_chord_indices_from_root = chord_indices_from_root

            scale_chord_indices = list(range(1, len(scale) + 1))
            print("key agnostic scale: ", scale)
            print("key: ", key)

            print("chord_indices_from_root: ", chord_indices_from_root)
            print("root_index: ", root_index)

            south_chord = Chord(chord_indices_from_root, chord_indices_from_root, root_index, scale)
            west_chord = Chord(no_root_chord_indices_from_root, chord_indices_from_root, root_index, scale)
            north_chord = Chord(scale_chord_indices, scale_chord_indices, 0, scale)
            east_chord = Chord(scale_chord_indices, scale_chord_indices, 0, scale)

            self.chords[ChordButton.SOUTH] = south_chord
            self.chords[ChordButton.WEST] = west_chord
            self.chords[ChordButton.NORTH] = north_chord
            self.chords[ChordButton.EAST] = east_chord

            self.update_chord_type()

    def get_scale_and_key(self, note_classes: list[int]) -> tuple[int, list[int]]:
        last_seven = state.note_in_history.classRecencyRanking[:7]
        for scale in state.preferred_scale_classes:
            possible_rotations: list[int] = []
            for r in range(12):
                rotated_scale = self.rotate_forward(r, scale)
                if self.notes_fit_in_scale(note_classes, rotated_scale):
                    possible_rotations.append(r)
            if len(possible_rotations) == 0:
                continue
            if len(possible_rotations) == 1:
                return possible_rotations[0], scale
            if (len(possible_rotations) > 1
                    and state.scale_mode == ExternalChordScaleMode.LAST_SEVEN):
                    if not self.notes_fit_in_scale(note_classes, last_seven):
                        return self.use_notes_as_scale(note_classes)
                    for r in possible_rotations:
                        rotated_scale = self.rotate_forward(r, scale)
                        if self.notes_fit_in_scale(last_seven, rotated_scale):
                            return r, scale
        if not self.notes_fit_in_scale(note_classes, last_seven):
            return self.use_notes_as_scale(note_classes)
        return self.use_notes_as_scale(last_seven)

    def use_notes_as_scale(self, note_classes: list[int]) -> tuple[int, list[int]]:
        if len(note_classes) == 0:
            return 0, []
        return note_classes[0], self.rotate_back(note_classes[0], note_classes)

    def notes_fit_in_scale(self, note_classes: list[int], scale: list[int]) -> bool:
        return all(chord_class in scale for chord_class in note_classes)

    def get_prime_form(self, note_classes: list[int]) -> list[int]:
        classes = list(note_classes)
        classes.sort()
        lowest_sum = 66
        prime_form = []

        for note in classes:
            rotated_classes = self.rotate_back(note, classes)
            rotated_classes.sort()
            rotation_sum = sum(rotated_classes)
            if rotation_sum < lowest_sum:
                lowest_sum = rotation_sum
                prime_form = rotated_classes

        return prime_form

    def rotate_back(self, r: int, note_classes: list[int]) -> list[int]:
        new_classes = [(note_class + (12 - r)) % 12 for note_class in note_classes]
        new_classes.sort()
        return new_classes

    def rotate_forward(self, r: int, note_classes: list[int]) -> list[int]:
        new_classes = [(note_class + r) % 12 for note_class in note_classes]
        new_classes.sort()
        return new_classes
