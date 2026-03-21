from redux import store
from redux.actions import musicEngine as actions

from ...chordEngineState import state
from ...utils import find_all_octaves_in_range


class Scale:

    def __init__(self):
        self.update(state.scale.key_agnostic)

    def update(self, scale):
        state.scale.key_agnostic = scale
        state.scale.note_class_map, state.scale.all_notes_map = self.__find_scale_notes()

        store.dispatch(actions.change_scale(state.scale.key_agnostic))

    def get(self):
        return state.scale.note_class_map[state.key.value]

    def __find_scale_notes_for_key(self, key):
        scale_notes = []
        for note in state.scale.key_agnostic:
            scale_notes.append((note + key) % 12)
        return scale_notes

    def __find_scale_notes(self):
        scale_notes = {}
        all_scale_notes = {}
        for key in range(12):
            scale_notes[key] = self.__find_scale_notes_for_key(key)
            all_scale_notes[key] = find_all_octaves_in_range(scale_notes[key])
        return scale_notes, all_scale_notes
