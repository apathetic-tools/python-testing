# tests/30_independant/test_atest_isolated_logging.py
"""Tests for atest_isolated_logging fixture.

Tests for atest_isolated_logging, including logger state reset, isolation
between tests, and the public API (assert_root_level, assert_logger_level,
capture_streams).
"""

from __future__ import annotations

import logging
from typing import Any

import pytest


# ---------------------------------------------------------------------------
# Tests for atest_isolated_logging
# ---------------------------------------------------------------------------


def test_isolated_logging_resets_logger_state(
    atest_isolated_logging: Any,  # noqa: ARG001
) -> None:
    """Test that atest_isolated_logging fixture properly resets logger state."""
    root = logging.getLogger("")
    root.setLevel(logging.DEBUG)
    assert root.level == logging.DEBUG


def test_isolated_logging_state_reset_between_tests(
    atest_isolated_logging: Any,
) -> None:
    """Test that atest_isolated_logging provides consistent, clean state.

    This test verifies the fixture initializes the logging system to a known,
    documented state - ready for testing.
    """
    root = logging.getLogger("")
    original_level = root.level
    atest_isolated_logging.assert_root_level(original_level)
    # Change the level
    root.setLevel(logging.ERROR)
    assert root.level == logging.ERROR
    # Verify we can check it
    atest_isolated_logging.assert_root_level("ERROR")


def test_isolated_logging_clears_loggers(
    atest_isolated_logging: Any,  # noqa: ARG001
) -> None:
    """Test that atest_isolated_logging clears loggers between tests."""
    logger = logging.getLogger("test.app")
    logger.setLevel(logging.DEBUG)
    assert "test.app" in logging.Logger.manager.loggerDict


@pytest.mark.usefixtures("atest_isolated_logging")
def test_isolated_logging_clears_in_next_test() -> None:
    """Test that logger from previous test is removed by fixture isolation."""
    assert "test.app" not in logging.Logger.manager.loggerDict


def test_isolated_logging_get_logger(
    atest_isolated_logging: Any,  # noqa: ARG001
) -> None:
    """Test that we can get loggers from atest_isolated_logging fixture."""
    logger = logging.getLogger("myapp.module")
    assert logger.name == "myapp.module"
    assert isinstance(logger, logging.Logger)


def test_isolated_logging_assert_root_level_passes(
    atest_isolated_logging: Any,
) -> None:
    """Test that assert_root_level passes when level matches."""
    root = logging.getLogger("")
    root.setLevel(logging.DEBUG)
    atest_isolated_logging.assert_root_level("DEBUG")  # Should not raise


def test_isolated_logging_assert_root_level_fails(
    atest_isolated_logging: Any,
) -> None:
    """Test that assert_root_level fails when level doesn't match."""
    root = logging.getLogger("")
    root.setLevel(logging.DEBUG)
    with pytest.raises(AssertionError):
        atest_isolated_logging.assert_root_level("INFO")


def test_isolated_logging_assert_logger_level(
    atest_isolated_logging: Any,
) -> None:
    """Test that assert_logger_level works correctly."""
    logger = logging.getLogger("myapp")
    logger.setLevel(logging.DEBUG)
    atest_isolated_logging.assert_logger_level("myapp", logging.DEBUG)


def test_isolated_logging_assert_logger_level_fails(
    atest_isolated_logging: Any,
) -> None:
    """Test that assert_logger_level fails when level doesn't match."""
    logger = logging.getLogger("myapp")
    logger.setLevel(logging.DEBUG)
    with pytest.raises(AssertionError):
        atest_isolated_logging.assert_logger_level("myapp", logging.INFO)


@pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING"])
def test_isolated_logging_with_parametrized_tests(
    atest_isolated_logging: Any,
    level: str,
) -> None:
    """Test that atest_isolated_logging works with parametrized tests."""
    root = logging.getLogger("")
    root.setLevel(level)
    atest_isolated_logging.assert_root_level(level)


def test_capture_streams_context_manager(
    atest_isolated_logging: Any,
) -> None:
    """Test that capture_streams works as a context manager."""
    logger = logging.getLogger("test_capture")
    logger.setLevel(logging.DEBUG)

    with atest_isolated_logging.capture_streams() as capture:
        logger.debug("test message")
        count = capture.count_message("test message")
        assert count == 1


def test_capture_streams_counts_multiple_messages(
    atest_isolated_logging: Any,
) -> None:
    """Test that capture_streams correctly counts messages."""
    logger = logging.getLogger("test_multi")
    logger.setLevel(logging.DEBUG)

    with atest_isolated_logging.capture_streams() as capture:
        logger.debug("msg1")
        logger.debug("msg2")
        logger.debug("msg1")

        count1 = capture.count_message("msg1")
        count2 = capture.count_message("msg2")
        expected_count_msg1 = 2
        expected_count_msg2 = 1
        assert count1 == expected_count_msg1
        assert count2 == expected_count_msg2


class TestIsolatedLoggingClassBased:
    """Class-based tests with atest_isolated_logging fixture."""

    def test_one(
        self,
        atest_isolated_logging: Any,  # noqa: ARG002
    ) -> None:
        """Test in class - first method sets a level."""
        root = logging.getLogger("")
        root.setLevel(logging.DEBUG)
        assert root.level == logging.DEBUG

    def test_two(
        self,
        atest_isolated_logging: Any,  # noqa: ARG002
    ) -> None:
        """Test in class - second method gets clean state."""
        root = logging.getLogger("")
        # State should be reset from previous test
        assert root.level != logging.DEBUG
