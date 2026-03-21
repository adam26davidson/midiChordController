"""Tests for chord display modulation animation positioning.

Bug: When modulating from Minor Nines scale [0, 2, 3, 5, 7, 8, 10] to
major [0, 2, 4, 5, 7, 9, 11] via left modulation, the scale shadows under
root (0) and fifth (7) visually move even though they map to themselves
(same index in both old and new scale). Only notes 3→4, 8→9, and 10→11
should animate.

The modulation animation uses index-based mapping in get_note_position():
  index = new_scale.index(note)
  old_note = old_scale[index]
For notes where old_note == note, there should be zero distance and no movement.
"""

import time
from unittest.mock import MagicMock, patch

from display.chord_display import ChordDisplay


# Minor Nines preset scales
MINOR_NINES_SCALE = [0, 2, 3, 5, 7, 8, 10]
MINOR_NINES_LEFT_MOD = [0, 2, 4, 5, 7, 9, 11]  # modal modulation result


class TestModulationAnimationPositioning:
    """Notes that exist at the same index in both old and new scales
    should not move during the modulation animation."""

    def _setup_modulation(self, old_scale, new_scale):
        cd = ChordDisplay(master=MagicMock())
        cd.set_scale(old_scale)
        cd.set_modulation(new_scale, "left")
        return cd

    def test_root_does_not_move_during_animation(self):
        """Root note (0) is at index 0 in both scales — should not move."""
        cd = self._setup_modulation(MINOR_NINES_SCALE, MINOR_NINES_LEFT_MOD)

        fixed_pos = cd.notes[0]["center"]
        animated_pos = cd.get_note_position(0)

        assert animated_pos["x"] == fixed_pos["x"], (
            f"Root x moved: fixed={fixed_pos['x']}, animated={animated_pos['x']}"
        )
        assert animated_pos["y"] == fixed_pos["y"], (
            f"Root y moved: fixed={fixed_pos['y']}, animated={animated_pos['y']}"
        )

    def test_fifth_does_not_move_during_animation(self):
        """Fifth note (7) is at index 4 in both scales — should not move."""
        cd = self._setup_modulation(MINOR_NINES_SCALE, MINOR_NINES_LEFT_MOD)

        fixed_pos = cd.notes[7]["center"]
        animated_pos = cd.get_note_position(7)

        assert animated_pos["x"] == fixed_pos["x"], (
            f"Fifth x moved: fixed={fixed_pos['x']}, animated={animated_pos['x']}"
        )
        assert animated_pos["y"] == fixed_pos["y"], (
            f"Fifth y moved: fixed={fixed_pos['y']}, animated={animated_pos['y']}"
        )

    def test_second_does_not_move_during_animation(self):
        """Second note (2) is at index 1 in both scales — should not move."""
        cd = self._setup_modulation(MINOR_NINES_SCALE, MINOR_NINES_LEFT_MOD)

        fixed_pos = cd.notes[2]["center"]
        animated_pos = cd.get_note_position(2)

        assert animated_pos["x"] == fixed_pos["x"]
        assert animated_pos["y"] == fixed_pos["y"]

    def test_fourth_does_not_move_during_animation(self):
        """Fourth note (5) is at index 3 in both scales — should not move."""
        cd = self._setup_modulation(MINOR_NINES_SCALE, MINOR_NINES_LEFT_MOD)

        fixed_pos = cd.notes[5]["center"]
        animated_pos = cd.get_note_position(5)

        assert animated_pos["x"] == fixed_pos["x"]
        assert animated_pos["y"] == fixed_pos["y"]

    def test_minor_third_animates_to_major_third(self):
        """Note 4 (major 3rd) in new scale was note 3 (minor 3rd) in old.
        It should animate FROM position 3 TO position 4."""
        cd = self._setup_modulation(MINOR_NINES_SCALE, MINOR_NINES_LEFT_MOD)

        old_pos = cd.notes[3]["center"]  # position of minor 3rd
        new_pos = cd.notes[4]["center"]  # position of major 3rd

        # These positions should differ (different notes on the circle)
        assert old_pos != new_pos, "Minor and major third should be at different positions"

        # At t=0, animated position should be at old position
        animated_pos = cd.get_note_position(4)
        # Allow some tolerance since time has advanced slightly since startTime
        assert animated_pos["x"] != new_pos["x"] or animated_pos["y"] != new_pos["y"], (
            "Note 4 should be animating from position 3, not already at position 4"
        )

    def test_all_stationary_notes_in_minor_nines_modulation(self):
        """Verify all notes that share the same index in old/new scales
        report zero animation distance."""
        cd = self._setup_modulation(MINOR_NINES_SCALE, MINOR_NINES_LEFT_MOD)

        # Notes that should NOT move (same value at same index)
        stationary_notes = []
        for i in range(len(MINOR_NINES_SCALE)):
            if MINOR_NINES_SCALE[i] == MINOR_NINES_LEFT_MOD[i]:
                stationary_notes.append(MINOR_NINES_LEFT_MOD[i])

        assert stationary_notes == [0, 2, 5, 7], (
            f"Expected [0, 2, 5, 7] to be stationary, got {stationary_notes}"
        )

        for note in stationary_notes:
            fixed_pos = cd.notes[note]["center"]
            animated_pos = cd.get_note_position(note)
            assert animated_pos["x"] == fixed_pos["x"] and \
                   animated_pos["y"] == fixed_pos["y"], (
                f"Note {note} should be stationary but moved: "
                f"fixed=({fixed_pos['x']}, {fixed_pos['y']}), "
                f"animated=({animated_pos['x']}, {animated_pos['y']})"
            )


class TestModulationAnimationMidway:
    """Test animation positions partway through the animation."""

    def test_stationary_notes_remain_fixed_midway(self):
        """Stationary notes should remain fixed even midway through animation."""
        cd = ChordDisplay(master=MagicMock())
        cd.set_scale(MINOR_NINES_SCALE)

        # Manually set modulation state with a start time in the past
        # to simulate being midway through the animation
        cd.modulation_state = {
            "side": "left",
            "oldScale": MINOR_NINES_SCALE,
            "newScale": MINOR_NINES_LEFT_MOD,
            "status": "startAnimation",
            "startTime": time.time() - (cd.mod_animation_length / 2),
        }

        for note in [0, 2, 5, 7]:
            fixed_pos = cd.notes[note]["center"]
            animated_pos = cd.get_note_position(note)
            assert animated_pos["x"] == fixed_pos["x"] and \
                   animated_pos["y"] == fixed_pos["y"], (
                f"Note {note} moved at animation midpoint"
            )

    def test_moving_notes_are_between_old_and_new_midway(self):
        """Moving notes should be partway between old and new position."""
        cd = ChordDisplay(master=MagicMock())
        cd.set_scale(MINOR_NINES_SCALE)

        cd.modulation_state = {
            "side": "left",
            "oldScale": MINOR_NINES_SCALE,
            "newScale": MINOR_NINES_LEFT_MOD,
            "status": "startAnimation",
            "startTime": time.time() - (cd.mod_animation_length / 2),
        }

        # Note 4 (major 3rd) animates from position 3 (minor 3rd)
        old_pos = cd.notes[3]["center"]
        new_pos = cd.notes[4]["center"]
        animated_pos = cd.get_note_position(4)

        # Should be between old and new, not at either endpoint
        if old_pos["x"] != new_pos["x"]:
            x_between = (min(old_pos["x"], new_pos["x"]) <= animated_pos["x"]
                        <= max(old_pos["x"], new_pos["x"]))
            assert x_between, (
                f"Note 4 x not between old and new: "
                f"old={old_pos['x']}, new={new_pos['x']}, animated={animated_pos['x']}"
            )


class TestRunAnimationStepPositioning:
    """Test that run_animation_step preserves positions of stationary notes."""

    def test_stationary_note_positions_preserved_after_animation_step(self):
        cd = ChordDisplay(master=MagicMock())
        cd.set_scale(MINOR_NINES_SCALE)
        cd.set_modulation(MINOR_NINES_LEFT_MOD, "left")

        # Record positions of stationary notes before animation step
        stationary_positions = {}
        for note in [0, 2, 5, 7]:
            pos = cd.get_note_position(note)
            stationary_positions[note] = (pos["x"], pos["y"])

        cd.run_animation_step()

        # Verify they haven't changed
        for note in [0, 2, 5, 7]:
            pos = cd.get_note_position(note)
            expected = stationary_positions[note]
            assert (pos["x"], pos["y"]) == expected, (
                f"Note {note} position changed after animation step: "
                f"before={expected}, after=({pos['x']}, {pos['y']})"
            )


