"""Tests for the default control map."""

from controller_coupler.control_maps.default_control_map import default_control_map


class TestDefaultControlMap:
    def test_chord_button_mappings_exist(self):
        all_params = []
        for param_keys in default_control_map.map.values():
            all_params.extend(param_keys)
        assert "INTERNAL_SOUTH_CHORD" in all_params
        assert "INTERNAL_WEST_CHORD" in all_params
        assert "INTERNAL_NORTH_CHORD" in all_params
        assert "INTERNAL_EAST_CHORD" in all_params

    def test_all_map_values_are_non_empty_lists(self):
        for key, value in default_control_map.map.items():
            assert isinstance(value, list), f"Map entry {key} is not a list"
            assert len(value) > 0, f"Map entry {key} is empty"
