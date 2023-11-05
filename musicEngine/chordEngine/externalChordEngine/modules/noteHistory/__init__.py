

import time
from typing import Dict, List
from ....chordEngineState import state


class HistoryUpdateResponse():
    lastContiguousClassesChanged: bool = False
    classesPlayedChanged: bool = False
    classRecencyRankingChanged: bool = False
    lowestChanged: bool = False


class NoteHistoryEvent():
    OnTime: int
    OffTime: int

    def __init__(self):
        self.OnTime = time.time_ns()
        self.OffTime = None
    
    def setOff(self):
        self.OffTime = time.time_ns()

    def durationSeconds(self) -> float:
        return (self.OffTime - self.OnTime) / 1000000000
    
    def endAgeSeconds(self) -> float:
        return (time.time_ns() - self.OffTime) / 1000000000
    
    def isOn(self) -> bool:
        return self.OffTime == None
    

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
            state.noteInHistory.all[noteClass].append(NoteHistoryEvent())
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
            state.noteInHistory.all[noteClass][-1].setOff()
        self.__removeExpired()

        return response

    def __removeExpired(self):
        for noteClassHistory in state.noteInHistory.all.values():
            for noteEvent in noteClassHistory:
                if noteEvent.endAgeSeconds() > state.noteInHistory.memoryLength:
                    noteClassHistory.remove(noteEvent)

    def __latestNoteIsOn(self, note: int) -> bool:
        if len(state.noteInHistory.all[note]) > 0:
            return state.noteInHistory.all[note][-1].isOn()
        return False
    
        