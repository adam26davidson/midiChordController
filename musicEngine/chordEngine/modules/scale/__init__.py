from ...utils import findAllOctavesInRange
from ...chordEngineState import state 
from redux import store
from redux.actions import musicEngine as actions

class Scale():

    def __init__(self):
        self.update(state.scale.keyAgnostic)

    def update(self, scale):
        state.scale.keyAgnostic = scale
        state.scale.noteClassMap, state.scale.allNotesMap = self.__findScaleNotes()

        store.dispatch(actions.changeScale(state.scale.keyAgnostic))

    def get(self):
        return state.scale.noteClassMap[state.key.value]

    def __findScaleNotesForKey(self, key):
        scaleNotes = []
        for note in state.scale.keyAgnostic:
            scaleNotes.append((note + key) % 12)
        return scaleNotes

    def __findScaleNotes(self):
        scaleNotes = {}
        allScaleNotes = {}
        for key in range(0, 12):
            scaleNotes[key] = self.__findScaleNotesForKey(key)
            allScaleNotes[key] = findAllOctavesInRange(scaleNotes[key])
        return scaleNotes, allScaleNotes