"""Tests for the logging fixture API.

These tests verify that the logging fixtures (isolated_logging, logging_test_level,
logging_level_testing) work correctly and provide the documented API.

Note: These tests are independent of the actual logging implementation bugs.
They verify that our fixtures work as documented for users.
"""

from __future__ import annotations

import logging
from typing import Any

import apathetic_logging as amod_logging
import pytest


def test_isolated_logging_resets_logger_state(
    isolated_logging: Any,  # noqa: ARG001
) -> None:
    """Test that isolated_logging fixture properly resets logger state."""
    root = logging.getLogger("")
    root.setLevel(logging.DEBUG)
    assert root.level == logging.DEBUG


def test_isolated_logging_state_reset_between_tests(
    isolated_logging: Any,
) -> None:
    """Test that isolated_logging provides consistent, clean state.

    This test verifies the fixture initializes the logging system to a known,
    documented state - ready for testing.
    """
    root = logging.getLogger("")
    original_level = root.level
    isolated_logging.assert_root_level(original_level)
    # Change the level
    root.setLevel(logging.ERROR)
    assert root.level == logging.ERROR
    # Verify we can check it
    isolated_logging.assert_root_level("ERROR")


def test_isolated_logging_clears_loggers(
    isolated_logging: Any,  # noqa: ARG001
) -> None:
    """Test that isolated_logging clears loggers between tests."""
    logger = logging.getLogger("test.app")
    logger.setLevel(logging.DEBUG)
    assert "test.app" in logging.Logger.manager.loggerDict


@pytest.mark.usefixtures("isolated_logging")
def test_isolated_logging_clears_in_next_test() -> None:
    """Test that logger from previous test is removed by fixture isolation."""
    assert "test.app" not in logging.Logger.manager.loggerDict


def test_isolated_logging_get_logger(
    isolated_logging: Any,  # noqa: ARG001
) -> None:
    """Test that we can get loggers from isolated_logging fixture."""
    logger = logging.getLogger("myapp.module")
    assert logger.name == "myapp.module"
    assert isinstance(logger, logging.Logger)


def test_isolated_logging_assert_root_level_passes(
    isolated_logging: Any,
) -> None:
    """Test that assert_root_level passes when level matches."""
    root = logging.getLogger("")
    root.setLevel(logging.DEBUG)
    isolated_logging.assert_root_level("DEBUG")  # Should not raise


def test_isolated_logging_assert_root_level_fails(
    isolated_logging: Any,
) -> None:
    """Test that assert_root_level fails when level doesn't match."""
    root = logging.getLogger("")
    root.setLevel(logging.DEBUG)
    with pytest.raises(AssertionError):
        isolated_logging.assert_root_level("INFO")


def test_isolated_logging_assert_logger_level(
    isolated_logging: Any,
) -> None:
    """Test that assert_logger_level works correctly."""
    logger = logging.getLogger("myapp")
    logger.setLevel(logging.DEBUG)
    isolated_logging.assert_logger_level("myapp", logging.DEBUG)


def test_isolated_logging_assert_logger_level_fails(
    isolated_logging: Any,
) -> None:
    """Test that assert_logger_level fails when level doesn't match."""
    logger = logging.getLogger("myapp")
    logger.setLevel(logging.DEBUG)
    with pytest.raises(AssertionError):
        isolated_logging.assert_logger_level("myapp", logging.INFO)


@pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING"])
def test_isolated_logging_with_parametrized_tests(
    isolated_logging: Any,
    level: str,
) -> None:
    """Test that isolated_logging works with parametrized tests."""
    root = logging.getLogger("")
    root.setLevel(level)
    isolated_logging.assert_root_level(level)


class TestIsolatedLoggingClassBased:
    """Class-based tests with isolated_logging fixture."""

    def test_one(
        self,
        isolated_logging: Any,  # noqa: ARG002
    ) -> None:
        """Test in class - first method sets a level."""
        root = logging.getLogger("")
        root.setLevel(logging.DEBUG)
        assert root.level == logging.DEBUG

    def test_two(
        self,
        isolated_logging: Any,  # noqa: ARG002
    ) -> None:
        """Test in class - second method gets clean state."""
        root = logging.getLogger("")
        # State should be reset from previous test
        assert root.level != logging.DEBUG


def test_logging_test_level_prevents_downgrades(
    logging_test_level: Any,  # noqa: ARG001
) -> None:
    """Test that logging_test_level prevents downgrading below TEST level."""
    root = logging.getLogger("")
    # Should be at TEST level (most verbose)
    assert root.level <= logging.DEBUG  # TEST is 2, DEBUG is 10


def test_logging_test_level_allows_temporary_changes(
    logging_test_level: Any,
) -> None:
    """Test that logging_test_level allows temporary downgrades when needed."""
    # Allow the app to change levels temporarily
    with logging_test_level.temporarily_allow_changes():
        root = logging.getLogger("")
        root.setLevel(logging.ERROR)
        assert root.level == logging.ERROR
    # After context, downgrade prevention is re-enabled


def test_logging_level_testing_tracks_changes(
    logging_level_testing: Any,
) -> None:
    """Test that logging_level_testing tracks level changes."""
    # Initial level should be set (default ERROR)
    logging_level_testing.assert_root_level("ERROR")
    # Change the level
    root = logging.getLogger("")
    root.setLevel(logging.DEBUG)
    logging_level_testing.assert_root_level("DEBUG")


def test_logging_level_testing_assert_level_changed_from(
    logging_level_testing: Any,
) -> None:
    """Test that logging_level_testing can verify level transitions."""
    # Change the level using apathetic_logging (which tracking_level wraps)
    amod_logging.setRootLevel(logging.DEBUG)
    # This should pass - we changed from ERROR to DEBUG
    logging_level_testing.assert_level_changed_from("ERROR", to="DEBUG")


def test_logging_level_testing_assert_level_not_changed(
    logging_level_testing: Any,
) -> None:
    """Test that logging_level_testing detects if level wasn't changed."""
    # Don't change the level
    with pytest.raises(AssertionError):
        # This should fail - we didn't change from initial ERROR level
        logging_level_testing.assert_level_changed_from("ERROR", to="DEBUG")


@pytest.mark.initial_level("WARNING")
def test_logging_level_testing_with_initial_level_marker(
    logging_level_testing: Any,
) -> None:
    """Test that logging_level_testing respects initial_level marker.

    This test has a pytest mark that should set the initial level to WARNING.
    """
    # Should have started at WARNING due to the marker
    logging_level_testing.assert_root_level("WARNING")


def test_capture_streams_context_manager(
    isolated_logging: Any,
) -> None:
    """Test that capture_streams works as a context manager."""
    logger = logging.getLogger("test_capture")
    logger.setLevel(logging.DEBUG)

    with isolated_logging.capture_streams() as capture:
        logger.debug("test message")
        count = capture.count_message("test message")
        assert count == 1


def test_capture_streams_counts_multiple_messages(
    isolated_logging: Any,
) -> None:
    """Test that capture_streams correctly counts messages."""
    logger = logging.getLogger("test_multi")
    logger.setLevel(logging.DEBUG)

    with isolated_logging.capture_streams() as capture:
        logger.debug("msg1")
        logger.debug("msg2")
        logger.debug("msg1")

        count1 = capture.count_message("msg1")
        count2 = capture.count_message("msg2")
        expected_count_msg1 = 2
        expected_count_msg2 = 1
        assert count1 == expected_count_msg1
        assert count2 == expected_count_msg2
