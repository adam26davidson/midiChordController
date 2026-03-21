"""Tests for the default control map."""

from controller_coupler.control_maps.default_control_map import default_control_map


class TestDefaultControlMap:
    def test_has_name(self):
        assert default_control_map.name is not None
        assert len(default_control_map.name) > 0

    def test_has_map(self):
        assert default_control_map.map is not None
        assert len(default_control_map.map) > 0

    def test_chord_button_mappings_exist(self):
        # The map should contain mappings for chord buttons
        all_params = []
        for param_keys in default_control_map.map.values():
            all_params.extend(param_keys)
        # Check that at least the south chord is mapped
        assert "INTERNAL_SOUTH_CHORD" in all_params

    def test_all_map_values_are_lists(self):
        for key, value in default_control_map.map.items():
            assert isinstance(value, list), f"Map entry {key} is not a list"

    def test_all_map_values_are_non_empty(self):
        for key, value in default_control_map.map.items():
            assert len(value) > 0, f"Map entry {key} is empty"
