# tests/30_independant/test_atest_logging_level_testing.py
"""Tests for atest_logging_level_testing fixture.

Tests for atest_logging_level_testing, including level change tracking,
assertions about level transitions, and initial level marker support.
"""

from __future__ import annotations

import logging
from typing import Any

import apathetic_logging as amod_logging
import pytest


# ---------------------------------------------------------------------------
# Tests for atest_logging_level_testing
# ---------------------------------------------------------------------------


def test_logging_level_testing_tracks_changes(
    atest_logging_level_testing: Any,
) -> None:
    """Test that atest_logging_level_testing tracks level changes."""
    # Initial level should be set (default ERROR)
    atest_logging_level_testing.assert_root_level("ERROR")
    # Change the level
    root = logging.getLogger("")
    root.setLevel(logging.DEBUG)
    atest_logging_level_testing.assert_root_level("DEBUG")


def test_logging_level_testing_assert_level_changed_from(
    atest_logging_level_testing: Any,
) -> None:
    """Test that atest_logging_level_testing can verify level transitions."""
    # Change the level using apathetic_logging (which tracking_level wraps)
    amod_logging.setRootLevel(logging.DEBUG)
    # This should pass - we changed from ERROR to DEBUG
    atest_logging_level_testing.assert_level_changed_from("ERROR", to="DEBUG")


def test_logging_level_testing_assert_level_not_changed(
    atest_logging_level_testing: Any,
) -> None:
    """Test that atest_logging_level_testing detects if level wasn't changed."""
    # Don't change the level
    with pytest.raises(AssertionError):
        # This should fail - we didn't change from initial ERROR level
        atest_logging_level_testing.assert_level_changed_from("ERROR", to="DEBUG")


@pytest.mark.initial_level("WARNING")
def test_logging_level_testing_with_initial_level_marker(
    atest_logging_level_testing: Any,
) -> None:
    """Test that atest_logging_level_testing respects initial_level marker.

    This test has a pytest mark that should set the initial level to WARNING.
    """
    # Should have started at WARNING due to the marker
    atest_logging_level_testing.assert_root_level("WARNING")
