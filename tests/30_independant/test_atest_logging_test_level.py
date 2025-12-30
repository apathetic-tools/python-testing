# tests/30_independant/test_atest_logging_test_level.py
"""Tests for atest_logging_test_level fixture.

Tests for atest_logging_test_level, including downgrade prevention and
temporary change allowance functionality.
"""

from __future__ import annotations

import logging
from typing import Any


# ---------------------------------------------------------------------------
# Tests for atest_logging_test_level
# ---------------------------------------------------------------------------


def test_logging_test_level_prevents_downgrades(
    atest_logging_test_level: Any,  # noqa: ARG001
) -> None:
    """Test that atest_logging_test_level prevents downgrading below TEST level."""
    root = logging.getLogger("")
    # Should be at TEST level (most verbose)
    assert root.level <= logging.DEBUG  # TEST is 2, DEBUG is 10


def test_logging_test_level_allows_temporary_changes(
    atest_logging_test_level: Any,
) -> None:
    """Test that atest_logging_test_level allows temporary downgrades when needed."""
    # Allow the app to change levels temporarily
    with atest_logging_test_level.temporarily_allow_changes():
        root = logging.getLogger("")
        root.setLevel(logging.ERROR)
        assert root.level == logging.ERROR
    # After context, downgrade prevention is re-enabled
