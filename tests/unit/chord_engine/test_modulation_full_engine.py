"""Test modulation with the full MusicEngine (both chord engines + MIDI pipeline).

Previous tests created InternalChordEngine in isolation. On the Pi, the full
MusicEngine is used, which creates both InternalChordEngine and
ExternalChordEngine, wires up the MIDI/rhythm pipeline, and may have
interactions that corrupt modulation state.
"""

from typing import Any, cast

import pytest

from models.command import Command
from music_engine import MusicEngine
from music_engine.chord_engine.chord_engine_state import state as engine_state
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
    """MusicEngine adds 100+ app parameters which pollutes the shared store
    for subsequent tests. Reset the coupler state after each test."""
    yield
    store.dispatch(me_actions.change_modulation({'scale': [], 'side': 'none'}))
    store.dispatch(cc_actions.update_app_parameters({}))
    engine_state.modulation.side = ModulationSide.NONE


def _create_music_engine():
    store.dispatch(me_actions.change_modulation({'scale': [], 'side': 'none'}))
    store.dispatch(me_actions.change_strum_mode('off'))
    engine_state.modulation.side = ModulationSide.NONE
    return MusicEngine()


class TestModulationWithFullEngine:
    """Test modulation using the full MusicEngine wiring."""

    def test_modulation_scale_correct_after_setting_load(self):
        """After loading Minor Nines via MusicEngine, the left modulation
        should have the correct scale."""
        me = _create_music_engine()
        me.internal_chord_engine.load_setting(MINOR_NINES_INDEX)

        left_mod = me.internal_chord_engine.modulations.get(ModulationSide.LEFT)
        assert left_mod is not None
        assert list(left_mod.scale) == MINOR_NINES_SCALE, (
            f"Modulation.scale = {list(left_mod.scale)}, "
            f"expected {MINOR_NINES_SCALE}"
        )

    def test_apply_to_scale_correct_with_full_engine(self):
        me = _create_music_engine()
        me.internal_chord_engine.load_setting(MINOR_NINES_INDEX)

        left_mod = me.internal_chord_engine.modulations.get(ModulationSide.LEFT)
        result = left_mod.apply_to_scale()
        assert result == MINOR_NINES_LEFT_MOD_SCALE, (
            f"apply_to_scale() = {result}, expected {MINOR_NINES_LEFT_MOD_SCALE}"
        )

    def test_modulation_after_navigating_settings(self):
        """Simulate the exact user flow: navigate through settings
        then trigger modulation."""
        me = _create_music_engine()

        # Navigate: Default(0) → Theiā(1) → No Fives(2) → Minor Nines(3)
        for i in [1, 2, 3]:
            me.internal_chord_engine.load_setting(i)

        left_mod = me.internal_chord_engine.modulations.get(ModulationSide.LEFT)
        assert list(left_mod.scale) == MINOR_NINES_SCALE, (
            f"After navigating settings, Modulation.scale = {list(left_mod.scale)}"
        )
        result = left_mod.apply_to_scale()
        assert result == MINOR_NINES_LEFT_MOD_SCALE, (
            f"apply_to_scale() = {result}, expected {MINOR_NINES_LEFT_MOD_SCALE}"
        )

    def test_modulation_after_chord_play_and_right_mod(self):
        """Full Pi flow: load setting, play chord, right mod, release,
        then left mod."""
        me = _create_music_engine()

        for i in [1, 2, 3]:
            me.internal_chord_engine.load_setting(i)

        ice = me.internal_chord_engine
        ice.chord_button_on(ChordButton.SOUTH)

        # Right modulation on/off
        ice.modulations.set(ModulationSide.RIGHT)
        ice.modulations.set(ModulationSide.NONE)

        # Left modulation
        left_mod = ice.modulations.get(ModulationSide.LEFT)
        assert list(left_mod.scale) == MINOR_NINES_SCALE, (
            f"Modulation.scale = {list(left_mod.scale)}, "
            f"expected {MINOR_NINES_SCALE}"
        )
        result = left_mod.apply_to_scale()
        assert result == MINOR_NINES_LEFT_MOD_SCALE, (
            f"apply_to_scale() = {result}, expected {MINOR_NINES_LEFT_MOD_SCALE}"
        )

    def test_state_scale_key_agnostic_stable(self):
        """state.scale.key_agnostic should remain the preset scale
        after all operations."""
        me = _create_music_engine()
        me.internal_chord_engine.load_setting(MINOR_NINES_INDEX)

        assert list(engine_state.scale.key_agnostic) == MINOR_NINES_SCALE

        ice = me.internal_chord_engine
        ice.chord_button_on(ChordButton.SOUTH)
        assert list(engine_state.scale.key_agnostic) == MINOR_NINES_SCALE

        ice.modulations.set(ModulationSide.LEFT)
        assert list(engine_state.scale.key_agnostic) == MINOR_NINES_SCALE, (
            f"state.scale.key_agnostic changed during modulation: "
            f"{list(engine_state.scale.key_agnostic)}"
        )

        ice.modulations.set(ModulationSide.NONE)
        assert list(engine_state.scale.key_agnostic) == MINOR_NINES_SCALE

    def test_scale_not_corrupted_by_external_engine_init(self):
        """ExternalChordEngine construction should not corrupt the
        InternalChordEngine's scale state."""
        me = _create_music_engine()
        me.internal_chord_engine.load_setting(MINOR_NINES_INDEX)

        # The ExternalChordEngine was already created in MusicEngine.__init__
        # Verify it didn't corrupt the scale
        assert list(engine_state.scale.key_agnostic) == MINOR_NINES_SCALE

        left_mod = me.internal_chord_engine.modulations.get(ModulationSide.LEFT)
        assert list(left_mod.scale) == MINOR_NINES_SCALE
        assert left_mod.scale is engine_state.scale.key_agnostic

    def test_coupler_syncs_parameters_after_setting_change(self):
        """Bug: ControllerCoupler must sync its parameter cache when
        parameters are replaced with the same keys (e.g., during
        load_setting). Previously it only synced when the count changed,
        causing stale lambdas from old Modulations instances to fire.

        After the fix, the coupler should always have the current
        parameters from the store."""

        me = _create_music_engine()

        # Load No Fives (scale = [0, 2, 4, 5, 7, 9, 11])
        me.internal_chord_engine.load_setting(2)

        # Capture the parameter from the store after No Fives
        old_left_mod = cast('Any', store.get_state()['controllerCoupler'])['appParameters']['LEFT_MODULATION']

        # Now load Minor Nines (scale = [0, 2, 3, 5, 7, 8, 10])
        me.internal_chord_engine.load_setting(MINOR_NINES_INDEX)

        # The store should have a NEW parameter (different object)
        new_left_mod = cast('Any', store.get_state()['controllerCoupler'])['appParameters']['LEFT_MODULATION']
        assert new_left_mod is not old_left_mod, (
            "Store should have a new LEFT_MODULATION parameter after setting change"
        )

        # Call the NEW parameter's ON command — should use Minor Nines scale
        new_left_mod.command_mappings[Command.ON]()

        from pyrsistent import thaw
        mod_state = cast('Any', thaw(store.get_state()['musicEngine']['modulation']))
        assert mod_state['scale'] == MINOR_NINES_LEFT_MOD_SCALE, (
            f"Dispatched modulation scale = {mod_state['scale']}, "
            f"expected {MINOR_NINES_LEFT_MOD_SCALE}"
        )

        # Verify calling the OLD parameter gives the WRONG result
        # (this proves the bug existed — stale parameters produce wrong scales)
        engine_state.modulation.side = ModulationSide.NONE
        old_left_mod.command_mappings[Command.ON]()
        mod_state = cast('Any', thaw(store.get_state()['musicEngine']['modulation']))
        assert mod_state['scale'] != MINOR_NINES_LEFT_MOD_SCALE, (
            "Old parameter should produce wrong scale (proving the bug)"
        )
