import music_engine.chord_engine.chord_engine_state as state_module
from music_engine.chord_engine.modules.scale import Scale


class TestScale:
    def test_default_chromatic_scale(self):
        scale = Scale()
        state_module.state.key.value = 0
        result = scale.get()
        assert result == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

    def test_major_scale_key_c(self):
        scale = Scale()
        scale.update([0, 2, 4, 5, 7, 9, 11])
        state_module.state.key.value = 0
        result = scale.get()
        assert result == [0, 2, 4, 5, 7, 9, 11]

    def test_major_scale_key_d(self):
        scale = Scale()
        scale.update([0, 2, 4, 5, 7, 9, 11])
        state_module.state.key.value = 2
        result = scale.get()
        # D major: D E F# G A B C# → 2 4 6 7 9 11 1
        assert sorted(result) == [1, 2, 4, 6, 7, 9, 11]

    def test_pentatonic_scale(self):
        scale = Scale()
        scale.update([0, 2, 4, 7, 9])
        state_module.state.key.value = 0
        result = scale.get()
        assert result == [0, 2, 4, 7, 9]

    def test_pentatonic_transposed_to_g(self):
        scale = Scale()
        scale.update([0, 2, 4, 7, 9])
        state_module.state.key.value = 7
        result = scale.get()
        expected = [(n + 7) % 12 for n in [0, 2, 4, 7, 9]]
        assert sorted(result) == sorted(expected)

    def test_update_changes_state(self):
        scale = Scale()
        assert state_module.state.scale.key_agnostic == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        scale.update([0, 2, 4, 5, 7, 9, 11])
        assert state_module.state.scale.key_agnostic == [0, 2, 4, 5, 7, 9, 11]

    def test_all_twelve_keys_populated(self):
        scale = Scale()
        scale.update([0, 2, 4, 5, 7, 9, 11])
        for key in range(12):
            state_module.state.key.value = key
            result = scale.get()
            assert len(result) == 7

    def test_scale_notes_wrap_correctly(self):
        scale = Scale()
        scale.update([0, 2, 4, 5, 7, 9, 11])
        state_module.state.key.value = 11  # B
        result = scale.get()
        # All should be 0-11
        assert all(0 <= n < 12 for n in result)
        assert len(result) == 7
