"""Tests for Inversion widget initialization.

Bug 2: draw_separators() was never called in __init__. With the old subscriber
approach, a Redux dispatch during init would eventually trigger it via
self.after(0, ...). With the dirty-flag refactor, check_state() sees no diff
(initial values match defaults) so separators are never drawn.
"""

from unittest.mock import MagicMock

from display.perform.inversion import Inversion


class TestInversionInit:

    def test_separators_created_after_init(self):
        inv = Inversion(master=MagicMock())
        assert len(inv.separators) > 0

    def test_separator_count_matches_max(self):
        inv = Inversion(master=MagicMock())
        assert len(inv.separators) == 2 * inv.max

    def test_default_max_is_three(self):
        inv = Inversion(master=MagicMock())
        assert inv.max == 3
        assert len(inv.separators) == 6


class TestInversionSetMax:

    def test_set_max_updates_separator_count(self):
        inv = Inversion(master=MagicMock())
        inv.set_max(5, 0)
        assert len(inv.separators) == 10

    def test_set_max_smaller_reduces_separators(self):
        inv = Inversion(master=MagicMock())
        inv.set_max(2, 0)
        assert len(inv.separators) == 4


class TestInversionSetActiveRegion:

    def test_set_active_region_preserves_separator_count(self):
        inv = Inversion(master=MagicMock())
        original_count = len(inv.separators)
        inv.set_active_region(2, "continuous")
        assert len(inv.separators) == original_count

    def test_set_active_region_repositions_without_recreating(self):
        """Separators should be repositioned, not deleted and recreated."""
        inv = Inversion(master=MagicMock())
        original_ids = list(inv.separators)
        inv.set_active_region(1, "continuous")
        assert inv.separators == original_ids
