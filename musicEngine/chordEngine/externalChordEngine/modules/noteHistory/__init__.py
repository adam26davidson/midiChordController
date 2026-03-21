

import time

from musicEngine.chordEngine.chordEngineState import state
from musicEngine.chordEngine.state.noteHistoryState import NoteHistoryEvent


class HistoryUpdateResponse:
    last_contiguous_classes_changed: bool = False
    classes_played_changed: bool = False
    class_recency_ranking_changed: bool = False
    lowest_changed: bool = False


class NoteHistory:

    def __init__(self):
        for note in range(12):
            state.note_in_history.all[note] = []

    def note_on(self, note: int) -> HistoryUpdateResponse:

        note_class = note % 12
        response = HistoryUpdateResponse()

        # update lastContiguousClasses
        if state.note_in_history.classesPlayed == []:
            state.note_in_history.lastContiguousClasses = [note_class]
            state.note_in_history.lastContiguous = [note]
            state.note_in_history.lowest_in_contiguous_classes = note
        elif note_class not in state.note_in_history.lastContiguousClasses:
            state.note_in_history.lastContiguousClasses.append(note_class)
            response.last_contiguous_classes_changed = True

        if note not in state.note_in_history.notesPlayed:
            state.note_in_history.notesPlayed.append(note)

        if note not in state.note_in_history.lastContiguous:
            state.note_in_history.lastContiguous.append(note)
            if note < state.note_in_history.lowest_in_contiguous_classes:
                state.note_in_history.lowest_in_contiguous_classes = note
                response.lowest_changed = True

        # update ClassesPlayed
        if (note_class) not in state.note_in_history.classesPlayed:
            state.note_in_history.classesPlayed.append(note_class)
            response.classes_played_changed = True

        # update ClassRecencyRanking
        if (note_class) in state.note_in_history.classRecencyRanking:
            if state.note_in_history.classRecencyRanking[0] != note_class:
                response.class_recency_ranking_changed = True
            state.note_in_history.classRecencyRanking.remove(note_class)
        state.note_in_history.classRecencyRanking.insert(0, note_class)

        # update note history
        if len(state.note_in_history.all[note_class]) == 0 or not self.__latest_note_is_on(note_class):
            state.note_in_history.all[note_class].append(NoteHistoryEvent(on_time = time.time_ns(), off_time = None))
        self.__remove_expired()


    def note_off(self, note: int) -> HistoryUpdateResponse:

        note_class = note % 12

        # update notes played
        if note in state.note_in_history.notesPlayed:
            state.note_in_history.notesPlayed.remove(note)

        # update classesPlayed
        note_classes = [n % 12 for n in state.note_in_history.notesPlayed]
        if note_class not in note_classes and note_class in state.note_in_history.classesPlayed:
            state.note_in_history.classesPlayed.remove(note_class)

        # update note history
        if len(state.note_in_history.all[note_class]) > 0 and self.__latest_note_is_on(note_class):
            state.note_in_history.all[note_class][-1].off_time = time.time_ns()
        self.__remove_expired()


    def __remove_expired(self):
        for note_class_history in state.note_in_history.all.values():
            for note_event in note_class_history:
                if note_event.off_time is None:
                    continue
                end_age_seconds = (time.time_ns() - note_event.off_time) / 1000000000
                if end_age_seconds > state.note_in_history.memory_length:
                    note_class_history.remove(note_event)

    def __latest_note_is_on(self, note: int) -> bool:
        if len(state.note_in_history.all[note]) > 0:
            return state.note_in_history.all[note][-1].off_time is None
        return False
