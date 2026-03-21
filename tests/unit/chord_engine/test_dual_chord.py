import music_engine.chord_engine.chord_engine_state as state_module
from music_engine.chord_engine.modules.chords.dual_chord import DualChord


class TestDualChord:
    def _make_setting(self):
        return {
            "main": [0, 4, 7],
            "mainBass": [0],
            "alternate": [0, 3, 7],
            "alternateBass": [0],
            "root": 0,
        }

    def test_main_chord_when_not_alternate(self):
        setting = self._make_setting()
        dc = DualChord(setting)
        state_module.state.alternate = False
        state_module.state.key.value = 0
        state_module.state.voice_count = 3

        result = dc.get_chord()
        pitch_classes = sorted({n % 12 for n in result})
        assert pitch_classes == [0, 4, 7]  # Major triad

    def test_alternate_chord_when_alternate(self):
        setting = self._make_setting()
        dc = DualChord(setting)
        state_module.state.alternate = True
        state_module.state.key.value = 0
        state_module.state.voice_count = 3

        result = dc.get_chord()
        pitch_classes = sorted({n % 12 for n in result})
        assert pitch_classes == [0, 3, 7]  # Minor triad

    def test_get_bass_main(self):
        setting = self._make_setting()
        dc = DualChord(setting)
        state_module.state.alternate = False
        state_module.state.key.value = 0

        bass = dc.get_bass()
        assert isinstance(bass, int)

    def test_get_root(self):
        setting = self._make_setting()
        dc = DualChord(setting)
        state_module.state.alternate = False
        state_module.state.key.value = 0

        root = dc.get_root()
        assert root == 0  # C

    def test_get_note_types(self):
        setting = self._make_setting()
        dc = DualChord(setting)
        state_module.state.alternate = False
        state_module.state.key.value = 0

        note_types = dc.get_note_types()
        assert sorted(note_types) == [0, 4, 7]

    def test_different_scale(self):
        setting = self._make_setting()
        major = [0, 2, 4, 5, 7, 9, 11]
        dc = DualChord(setting, scale=major)
        state_module.state.alternate = False
        state_module.state.key.value = 0
        state_module.state.voice_count = 3

        result = dc.get_chord()
        assert len(result) == 3
