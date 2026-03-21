"""Integration test: verify the chord display captures correct old/new scales
during modulation, using the real chord engine flow.

Bug: The dim scale circles animate to wrong positions during modulation.
This test checks that chord_display.modulation_state captures the correct
oldScale and newScale values when processing a real modulation through
check_state.
"""

from unittest.mock import MagicMock, patch

from pyrsistent import thaw

from display.perform.perform_frame import PerformFrame
from music_engine.chord_engine.internal_chord_engine import InternalChordEngine
from music_engine.chord_engine.chord_engine_state import state as engine_state
from music_engine.chord_engine.state.chords_state import ChordButton
from music_engine.chord_engine.state.modulations_state import ModulationSide
from redux import store


MINOR_NINES_INDEX = 3
MINOR_NINES_SCALE = [0, 2, 3, 5, 7, 8, 10]
MINOR_NINES_LEFT_MOD_SCALE = [0, 2, 4, 5, 7, 9, 11]


def _create_engine():
    from redux.actions import music_engine as me_actions
    # Reset modulation to none to avoid pollution from prior tests
    store.dispatch(me_actions.change_modulation({'scale': [], 'side': 'none'}))
    engine = InternalChordEngine()
    engine.subscribe(lambda msg: None)
    return engine


class TestModulationScaleCapture:
    """Verify that chord_display captures the correct old and new scales."""

    def test_chord_display_scale_before_modulation(self):
        """Before modulation, chord_display.scale_notes should match
        the Minor Nines scale."""
        engine = _create_engine()
        engine.load_setting(MINOR_NINES_INDEX)

        pf = PerformFrame(container=MagicMock())
        pf._dirty = True
        pf.check_state()

        assert list(pf.chord_display.scale_notes) == MINOR_NINES_SCALE, (
            f"chord_display.scale_notes = {pf.chord_display.scale_notes}, "
            f"expected {MINOR_NINES_SCALE}"
        )

    def test_old_scale_captured_correctly(self):
        """When modulation triggers, oldScale in modulation_state should
        be the original Minor Nines scale, not the modulated scale."""
        engine = _create_engine()
        engine.load_setting(MINOR_NINES_INDEX)

        pf = PerformFrame(container=MagicMock())
        pf._dirty = True
        pf.check_state()

        # Verify pre-modulation state
        assert list(pf.chord_display.scale_notes) == MINOR_NINES_SCALE

        # Activate modulation
        engine.chord_button_on(ChordButton.SOUTH)
        engine.modulations.set(ModulationSide.LEFT)

        # Capture what set_modulation receives
        captured_old = None
        captured_new = None
        original_set_mod = pf.chord_display.set_modulation

        def capture_set_mod(new_scale, side):
            nonlocal captured_old, captured_new
            captured_old = list(pf.chord_display.scale_notes)
            captured_new = list(new_scale)
            return original_set_mod(new_scale, side)

        with patch.object(pf.chord_display, "set_modulation",
                          side_effect=capture_set_mod):
            pf._dirty = True
            pf.check_state()

        assert captured_old is not None, "set_modulation was never called"
        assert captured_old == MINOR_NINES_SCALE, (
            f"oldScale captured wrong: {captured_old}, expected {MINOR_NINES_SCALE}"
        )
        assert captured_new == MINOR_NINES_LEFT_MOD_SCALE, (
            f"newScale captured wrong: {captured_new}, expected {MINOR_NINES_LEFT_MOD_SCALE}"
        )

    def test_modulation_state_has_correct_scales(self):
        """After check_state processes modulation, modulation_state should
        have the correct old and new scales."""
        engine = _create_engine()
        engine.load_setting(MINOR_NINES_INDEX)

        pf = PerformFrame(container=MagicMock())
        pf._dirty = True
        pf.check_state()

        engine.chord_button_on(ChordButton.SOUTH)
        engine.modulations.set(ModulationSide.LEFT)
        pf._dirty = True
        pf.check_state()

        ms = pf.chord_display.modulation_state
        assert ms["status"] == "startAnimation"
        assert list(ms["oldScale"]) == MINOR_NINES_SCALE, (
            f"modulation_state oldScale = {ms['oldScale']}, "
            f"expected {MINOR_NINES_SCALE}"
        )
        assert list(ms["newScale"]) == MINOR_NINES_LEFT_MOD_SCALE, (
            f"modulation_state newScale = {ms['newScale']}, "
            f"expected {MINOR_NINES_LEFT_MOD_SCALE}"
        )

    def test_animation_index_mapping(self):
        """Verify the index-based animation mapping: for each note in
        newScale, the note at the same index in oldScale is where it
        should animate FROM."""
        engine = _create_engine()
        engine.load_setting(MINOR_NINES_INDEX)

        pf = PerformFrame(container=MagicMock())
        pf._dirty = True
        pf.check_state()

        engine.chord_button_on(ChordButton.SOUTH)
        engine.modulations.set(ModulationSide.LEFT)
        pf._dirty = True
        pf.check_state()

        ms = pf.chord_display.modulation_state
        old = ms["oldScale"]
        new = ms["newScale"]

        # Expected mapping for Minor Nines left modulation:
        expected_mapping = {
            0: 0,   # root stays
            2: 2,   # 2nd stays
            4: 3,   # major 3rd from minor 3rd
            5: 5,   # 4th stays
            7: 7,   # 5th stays
            9: 8,   # major 6th from minor 6th
            11: 10,  # major 7th from minor 7th
        }

        for new_note, expected_old_note in expected_mapping.items():
            idx = list(new).index(new_note)
            actual_old_note = old[idx]
            assert actual_old_note == expected_old_note, (
                f"Note {new_note} should animate from {expected_old_note}, "
                f"but old[{idx}]={actual_old_note}. "
                f"old={list(old)}, new={list(new)}"
            )

    def test_stationary_notes_have_zero_distance(self):
        """Notes that map to themselves should have zero animation distance."""
        engine = _create_engine()
        engine.load_setting(MINOR_NINES_INDEX)

        pf = PerformFrame(container=MagicMock())
        pf._dirty = True
        pf.check_state()

        engine.chord_button_on(ChordButton.SOUTH)
        engine.modulations.set(ModulationSide.LEFT)
        pf._dirty = True
        pf.check_state()

        cd = pf.chord_display
        # These notes should NOT move (same value at same index)
        for note in [0, 2, 5, 7]:
            fixed = cd.notes[note]["center"]
            animated = cd.get_note_position(note)
            assert animated["x"] == fixed["x"] and animated["y"] == fixed["y"], (
                f"Stationary note {note} has wrong position: "
                f"fixed=({fixed['x']:.1f}, {fixed['y']:.1f}), "
                f"animated=({animated['x']:.1f}, {animated['y']:.1f})"
            )
