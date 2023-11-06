

import time
from musicEngine.chordEngine.chordEngineState import state
from musicEngine.chordEngine.state.noteHistoryState import NoteHistoryEvent


class HistoryUpdateResponse():
    lastContiguousClassesChanged: bool = False
    classesPlayedChanged: bool = False
    classRecencyRankingChanged: bool = False
    lowestChanged: bool = False
    

class NoteHistory():

    def __init__(self):
        for note in range(0, 12):
            state.noteInHistory.all[note] = []

    def noteOn(self, note: int) -> HistoryUpdateResponse:

        noteClass = note % 12
        response = HistoryUpdateResponse()

        # update lastContiguousClasses
        if state.noteInHistory.classesPlayed == []:
            state.noteInHistory.lastContiguousClasses = [noteClass]
            state.noteInHistory.lastContiguous = [note]
            state.noteInHistory.lowestInContiguousClasses = note
            response.lastContiguousClassesChanged = True
            response.lowestChanged = True
        elif noteClass not in state.noteInHistory.lastContiguousClasses:
            state.noteInHistory.lastContiguousClasses.append(noteClass)
            response.lastContiguousClassesChanged = True
        elif note not in state.noteInHistory.lastContiguous:
            state.noteInHistory.lastContiguous.append(note)
            if note < state.noteInHistory.lowestInContiguousClasses:
                state.noteInHistory.lowestInContiguousClasses = note
                response.lowestChanged = True

        # update ClassesPlayed
        if (noteClass) not in state.noteInHistory.classesPlayed:
            state.noteInHistory.classesPlayed.append(noteClass)
            response.classesPlayedChanged = True

        # update ClassRecencyRanking
        if (noteClass) in state.noteInHistory.classRecencyRanking:
            if state.noteInHistory.classRecencyRanking[0] != noteClass:
                response.classRecencyRankingChanged = True
            state.noteInHistory.classRecencyRanking.remove(noteClass)
        state.noteInHistory.classRecencyRanking.insert(0, noteClass)

        # update note history
        if len(state.noteInHistory.all[noteClass]) == 0 or not self.__latestNoteIsOn(noteClass):
            state.noteInHistory.all[noteClass].append(NoteHistoryEvent(OnTime = time.time_ns(), OffTime = None))
        self.__removeExpired()

        return response

    def noteOff(self, note: int) -> HistoryUpdateResponse:

        noteClass = note % 12
        response = HistoryUpdateResponse()

        # update classesPlayed
        if (noteClass) in state.noteInHistory.classesPlayed:
            state.noteInHistory.classesPlayed.remove(noteClass)
            response.classesPlayedChanged = True
        
        # update lastContiguousClasses
        if len(state.noteInHistory.all[noteClass]) > 0 and self.__latestNoteIsOn(noteClass):
            state.noteInHistory.all[noteClass][-1].OffTime = time.time_ns()
        self.__removeExpired()

        return response

    def __removeExpired(self):
        for noteClassHistory in state.noteInHistory.all.values():
            for noteEvent in noteClassHistory:
                endAgeSeconds = (time.time_ns() - noteEvent.OffTime) / 1000000000
                if endAgeSeconds > state.noteInHistory.memoryLength:
                    noteClassHistory.remove(noteEvent)

    def __latestNoteIsOn(self, note: int) -> bool:
        if len(state.noteInHistory.all[note]) > 0:
            return state.noteInHistory.all[note][-1].OffTime == None
        return False
    
        