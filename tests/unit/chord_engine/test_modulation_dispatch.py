"""Test that the chord engine dispatches correct scale values during modulation.

Bug hypothesis: The scale dispatched in the change_modulation action is wrong,
causing the display to animate to incorrect positions.

For Minor Nines (scale [0, 2, 3, 5, 7, 8, 10]) with left modal modulation
(map [2, 0]), the modulated scale should be [0, 2, 4, 5, 7, 9, 11].
"""

from unittest.mock import patch

import pytest
from pyrsistent import thaw

from music_engine.chord_engine.chord_engine_state import state as engine_state
from music_engine.chord_engine.internal_chord_engine import InternalChordEngine
from music_engine.chord_engine.state.chords_state import ChordButton
from music_engine.chord_engine.state.modulations_state import ModulationSide
from redux import store
from redux.actions import controller_coupler as cc_actions
from redux.actions import music_engine as me_actions

MINOR_NINES_INDEX = 3
MINOR_NINES_SCALE = [0, 2, 3, 5, 7, 8, 10]
MINOR_NINES_LEFT_MOD_SCALE = [0, 2, 4, 5, 7, 9, 11]


@pytest.fixture(autouse=True)
def _reset_store_after_test():
    yield
    store.dispatch(me_actions.change_modulation({'scale': [], 'side': 'none'}))
    store.dispatch(cc_actions.update_app_parameters({}))
    engine_state.modulation.side = ModulationSide.NONE


def _create_engine():
    store.dispatch(me_actions.change_modulation({'scale': [], 'side': 'none'}))
    engine_state.modulation.side = ModulationSide.NONE
    engine = InternalChordEngine()
    engine.subscribe(lambda msg: None)
    return engine


class TestModulationObjectState:
    """Verify the Modulation object has correct internal state."""

    def test_modulation_scale_matches_setting(self):
        """Modulation.self.scale should be the original setting scale."""
        engine = _create_engine()
        engine.load_setting(MINOR_NINES_INDEX)

        left_mod = engine.modulations.get(ModulationSide.LEFT)
        assert left_mod is not None
        assert left_mod.scale == MINOR_NINES_SCALE, (
            f"Modulation.scale = {left_mod.scale}, expected {MINOR_NINES_SCALE}"
        )

    def test_modulation_map_correct(self):
        """The modal map should be the correct scale rotation."""
        engine = _create_engine()
        engine.load_setting(MINOR_NINES_INDEX)

        left_mod = engine.modulations.get(ModulationSide.LEFT)
        assert left_mod.map == MINOR_NINES_LEFT_MOD_SCALE, (
            f"Modulation.map = {left_mod.map}, expected {MINOR_NINES_LEFT_MOD_SCALE}"
        )

    def test_apply_to_scale_correct(self):
        """apply_to_scale should return the modulated scale."""
        engine = _create_engine()
        engine.load_setting(MINOR_NINES_INDEX)

        left_mod = engine.modulations.get(ModulationSide.LEFT)
        result = left_mod.apply_to_scale()
        assert result == MINOR_NINES_LEFT_MOD_SCALE, (
            f"apply_to_scale() = {result}, expected {MINOR_NINES_LEFT_MOD_SCALE}"
        )

    def test_offsets_correct(self):
        """Offsets should show which notes move and by how much."""
        engine = _create_engine()
        engine.load_setting(MINOR_NINES_INDEX)

        left_mod = engine.modulations.get(ModulationSide.LEFT)
        expected_offsets = [0, 0, 1, 0, 0, 1, 1]
        assert left_mod.offsets == expected_offsets, (
            f"offsets = {left_mod.offsets}, expected {expected_offsets}"
        )

    def test_modulation_scale_not_mutated_after_use(self):
        """Modulation.self.scale should not be mutated by any operation."""
        engine = _create_engine()
        engine.load_setting(MINOR_NINES_INDEX)

        left_mod = engine.modulations.get(ModulationSide.LEFT)
        original = list(left_mod.scale)

        # Press chord and activate modulation
        engine.chord_button_on(ChordButton.SOUTH)
        engine.modulations.set(ModulationSide.LEFT)

        assert left_mod.scale == original, (
            f"Modulation.scale mutated: was {original}, now {left_mod.scale}"
        )

    def test_state_scale_key_agnostic_not_mutated(self):
        """state.scale.key_agnostic should not change during modulation."""
        engine = _create_engine()
        engine.load_setting(MINOR_NINES_INDEX)

        original = list(engine_state.scale.key_agnostic)

        engine.chord_button_on(ChordButton.SOUTH)
        engine.modulations.set(ModulationSide.LEFT)

        assert list(engine_state.scale.key_agnostic) == original, (
            f"state.scale.key_agnostic changed: was {original}, "
            f"now {list(engine_state.scale.key_agnostic)}"
        )


class TestModulationDispatchedValues:
    """Verify the Redux actions dispatched during modulation have correct values."""

    def test_modulation_action_scale(self):
        """The change_modulation action should carry the modulated scale."""
        engine = _create_engine()
        engine.load_setting(MINOR_NINES_INDEX)
        engine.chord_button_on(ChordButton.SOUTH)

        dispatched = []
        original_dispatch = store.dispatch

        def record(action):
            dispatched.append(action)
            return original_dispatch(action)

        with patch.object(store, "dispatch", side_effect=record):
            engine.modulations.set(ModulationSide.LEFT)

        mod_actions = [a for a in dispatched if a["type"] == "me/modulationChanged"]
        assert len(mod_actions) == 1, f"Expected 1 modulation action, got {len(mod_actions)}"

        mod_scale = mod_actions[0]["data"]["modulation"]["scale"]
        assert mod_scale == MINOR_NINES_LEFT_MOD_SCALE, (
            f"Dispatched modulation scale = {mod_scale}, "
            f"expected {MINOR_NINES_LEFT_MOD_SCALE}"
        )

    def test_redux_scale_unchanged_during_modulation(self):
        """The Redux musicEngine.scale should NOT change during modulation."""
        engine = _create_engine()
        engine.load_setting(MINOR_NINES_INDEX)

        scale_before = thaw(store.get_state()["musicEngine"]["scale"])
        assert scale_before == MINOR_NINES_SCALE

        engine.chord_button_on(ChordButton.SOUTH)
        engine.modulations.set(ModulationSide.LEFT)

        scale_after = thaw(store.get_state()["musicEngine"]["scale"])
        assert scale_after == MINOR_NINES_SCALE, (
            f"Redux scale changed: {scale_before} → {scale_after}"
        )

    def test_full_dispatch_sequence(self):
        """Record all action types dispatched during modulation."""
        engine = _create_engine()
        engine.load_setting(MINOR_NINES_INDEX)
        engine.chord_button_on(ChordButton.SOUTH)

        dispatched_types = []
        original_dispatch = store.dispatch

        def record(action):
            dispatched_types.append(action["type"])
            return original_dispatch(action)

        with patch.object(store, "dispatch", side_effect=record):
            engine.modulations.set(ModulationSide.LEFT)

        print(f"Dispatch sequence: {dispatched_types}")
        # Should include modulation change and chord type change
        assert "me/modulationChanged" in dispatched_types
        # Should NOT include scale change
        assert "me/scaleChanged" not in dispatched_types, (
            "Scale should not be dispatched during modulation"
        )


class TestModulationAndDemodulation:
    """Test that modulation and demodulation produce correct states."""

    def test_demodulation_dispatches_original_scale(self):
        """When modulation returns to NONE, the dispatched modulation scale
        should be the original key_agnostic scale."""
        engine = _create_engine()
        engine.load_setting(MINOR_NINES_INDEX)
        engine.chord_button_on(ChordButton.SOUTH)

        # Activate modulation
        engine.modulations.set(ModulationSide.LEFT)

        # Deactivate
        dispatched = []
        original_dispatch = store.dispatch

        def record(action):
            dispatched.append(action)
            return original_dispatch(action)

        with patch.object(store, "dispatch", side_effect=record):
            engine.modulations.set(ModulationSide.NONE)

        mod_actions = [a for a in dispatched if a["type"] == "me/modulationChanged"]
        assert len(mod_actions) == 1

        # When returning to NONE, scale should be the original
        demod_scale = mod_actions[0]["data"]["modulation"]["scale"]
        assert demod_scale == MINOR_NINES_SCALE, (
            f"Demodulation scale = {demod_scale}, expected {MINOR_NINES_SCALE}"
        )

    def test_remodulation_after_demodulation(self):
        """After demodulating and remodulating, the modulation scale
        should still be correct."""
        engine = _create_engine()
        engine.load_setting(MINOR_NINES_INDEX)
        engine.chord_button_on(ChordButton.SOUTH)

        # Modulate → demodulate → modulate again
        engine.modulations.set(ModulationSide.LEFT)
        engine.modulations.set(ModulationSide.NONE)

        dispatched = []
        original_dispatch = store.dispatch

        def record(action):
            dispatched.append(action)
            return original_dispatch(action)

        with patch.object(store, "dispatch", side_effect=record):
            engine.modulations.set(ModulationSide.LEFT)

        mod_actions = [a for a in dispatched if a["type"] == "me/modulationChanged"]
        mod_scale = mod_actions[0]["data"]["modulation"]["scale"]
        assert mod_scale == MINOR_NINES_LEFT_MOD_SCALE, (
            f"Re-modulation scale = {mod_scale}, "
            f"expected {MINOR_NINES_LEFT_MOD_SCALE}"
        )

    def test_modulation_scale_reference_stability(self):
        """Modulation.self.scale should reference the same list as
        state.scale.key_agnostic (from construction time) and both
        should be the original scale."""
        engine = _create_engine()
        engine.load_setting(MINOR_NINES_INDEX)

        left_mod = engine.modulations.get(ModulationSide.LEFT)

        # Both should be the same object (same reference)
        assert left_mod.scale is engine_state.scale.key_agnostic, (
            "Modulation.scale is not the same object as state.scale.key_agnostic"
        )
        assert list(left_mod.scale) == MINOR_NINES_SCALE
