"""Pytest fixtures and helper classes for logging test isolation.

This module provides helper classes and pytest fixtures for the logging module.
The actual logging utilities are in the logging module; this module focuses on
the pytest integration and fixture lifecycle management.
"""

from __future__ import annotations

import logging
import time
import types
import uuid
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any, Literal

import apathetic_logging
import pytest
from typing_extensions import Self

from apathetic_testing.logging import ApatheticTest_Internal_Logging


# ============================================================================
# Fixtures Mixin
# ============================================================================


class ApatheticTest_Internal_Fixtures:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class providing fixture-related utilities.

    **Public Helper Classes:**
    - ``LoggingTestLevel`` - Helper for the atest_logging_test_level fixture
    - ``LoggingLevelTesting`` - Helper for the atest_logging_level_testing fixture
    """

    class LoggingTestLevel:
        """Helper object for the logging_test_level fixture.

        Prevents the root logger level from being downgraded below TEST level.
        """

        def __init__(
            self,
            isolation: ApatheticTest_Internal_Fixtures.LoggingIsolation,
            monkeypatch: pytest.MonkeyPatch,
        ) -> None:
            """Initialize and enforce TEST level.

            Args:
                isolation: The LoggingIsolation helper.
                monkeypatch: pytest's monkeypatch fixture.
            """
            self._isolation = isolation
            self._monkeypatch = monkeypatch
            self._prevention_enabled = True
            self._original_set_root_level = apathetic_logging.setRootLevel

            # Set root to TEST level
            apathetic_logging.setRootLevel(apathetic_logging.TEST_LEVEL)

            # Install monkey-patch to prevent downgrades
            self._install_prevention()

        def _install_prevention(self) -> None:
            """Install monkey-patch to enforce TEST as minimum log level.

            TEST is the lowest practical log level (value 2, below DEBUG=10),
            so no actual prevention is needed - any level change will either
            stay at TEST or go more verbose. This is a no-op that documents
            the contract: TEST level is maintained throughout the test.

            Uses patch_everywhere to work correctly in both package and stitched
            builds, ensuring the patch is applied to all locations where
            setRootLevel is referenced.
            """

            def protectedSetRootLevel(  # noqa: N802
                level: str | int, **kwargs: Any
            ) -> None:
                """Wrapper that maintains TEST as the minimum log level.

                Since TEST (2) is below all practical levels (DEBUG=10 and up),
                when prevention is enabled we just return (level stays at TEST).
                When prevention is disabled, we allow the level change.
                """
                if self._prevention_enabled:
                    return

                self._original_set_root_level(level, **kwargs)

            from .patch import ApatheticTest_Internal_Patch  # noqa: PLC0415

            ApatheticTest_Internal_Patch.patch_everywhere(
                self._monkeypatch,
                apathetic_logging,
                "setRootLevel",
                protectedSetRootLevel,
                package_prefix="apathetic_logging",
            )

        def allow_app_level_change(self) -> None:
            """Temporarily allow the app to change the log level.

            This disables the prevention mechanism, allowing setRootLevel to
            work normally for the rest of the test or until
            prevent_app_level_change() is called.
            """
            self._prevention_enabled = False

        def prevent_app_level_change(self) -> None:
            """Re-enable the prevention mechanism.

            This re-enables the monkey-patch that prevents downgrades.
            """
            self._prevention_enabled = True

        def get_current_level(self) -> int:
            """Get the current root logger level.

            Returns:
                The numeric log level of the root logger.
            """
            return apathetic_logging.getRootLogger().level

        @contextmanager
        def temporarily_allow_changes(self) -> Generator[None, None, None]:
            """Context manager to temporarily allow level changes.

            Example:
                with logging_test_level.temporarily_allow_changes():
                    app.configure_logging(level="INFO")
            """
            self.allow_app_level_change()
            try:
                yield
            finally:
                self.prevent_app_level_change()

    class LoggingLevelTesting:
        """Helper object for the atest_logging_level_testing fixture.

        Tracks log level changes for testing that your app sets levels
        correctly.
        """

        def __init__(
            self,
            isolation: ApatheticTest_Internal_Fixtures.LoggingIsolation,
            initial_level: str | int,
            monkeypatch: pytest.MonkeyPatch,
        ) -> None:
            """Initialize level testing helper.

            Args:
                isolation: The LoggingIsolation helper.
                initial_level: The initial root logger level.
                monkeypatch: pytest's monkeypatch fixture.
            """
            self._isolation = isolation
            self._initial_level_str = (
                initial_level if isinstance(initial_level, str) else str(initial_level)
            )
            self._initial_level_int = (
                apathetic_logging.getLevelNumber(initial_level)
                if isinstance(initial_level, str)
                else initial_level
            )
            self._monkeypatch = monkeypatch
            self._history: list[tuple[float, int, str]] = []

            # Set initial level
            apathetic_logging.setRootLevel(initial_level)
            self._record_level(self._initial_level_int)

            # Install monkey-patch to track changes
            self._original_set_root_level = apathetic_logging.setRootLevel
            self._install_tracking()

        def _install_tracking(self) -> None:
            """Install monkey-patch to track level changes.

            Uses patch_everywhere to work correctly in both package and stitched
            builds, ensuring the patch is applied to all locations where
            setRootLevel is referenced.
            """

            def trackedSetRootLevel(  # noqa: N802
                level: str | int, **kwargs: Any
            ) -> None:
                """Wrapper that tracks level changes."""
                self._original_set_root_level(level, **kwargs)

                # Record the new level
                if isinstance(level, str):
                    level_int = apathetic_logging.getLevelNumber(level)
                else:
                    level_int = level

                self._record_level(level_int)

            from .patch import ApatheticTest_Internal_Patch  # noqa: PLC0415

            ApatheticTest_Internal_Patch.patch_everywhere(
                self._monkeypatch,
                apathetic_logging,
                "setRootLevel",
                trackedSetRootLevel,
                package_prefix="apathetic_logging",
            )

        def _record_level(self, level_int: int) -> None:
            """Record a level change to the history.

            Args:
                level_int: The numeric level value.
            """
            level_name = apathetic_logging.getLevelNameStr(level_int)
            timestamp = time.time()
            self._history.append((timestamp, level_int, level_name))

        def assert_root_level(self, expected: str | int) -> None:
            """Assert that the root logger currently has the expected level.

            Args:
                expected: The expected log level (string or int).

            Raises:
                AssertionError: If the levels don't match.
            """
            self._isolation.assert_root_level(expected)

        def assert_level_changed_from(
            self,
            old_level: str | int,
            *,
            to: str | int,
        ) -> None:
            """Assert that the level changed from one value to another.

            Args:
                old_level: The previous level.
                to: The new level.

            Raises:
                AssertionError: If the transition wasn't found in history.
            """
            old_int = (
                apathetic_logging.getLevelNumber(old_level)
                if isinstance(old_level, str)
                else old_level
            )
            to_int = apathetic_logging.getLevelNumber(to) if isinstance(to, str) else to

            # Look for the transition in history
            for i in range(len(self._history) - 1):
                if self._history[i][1] == old_int and self._history[i + 1][1] == to_int:
                    return  # Found it

            # Not found, raise error
            old_name = apathetic_logging.getLevelNameStr(old_int)
            to_name = apathetic_logging.getLevelNameStr(to_int)
            history_names = [h[2] for h in self._history]
            msg = (
                f"Expected level change from {old_name} to {to_name}, "
                f"but history is: {history_names}"
            )
            raise AssertionError(msg)

        def assert_level_not_changed(self) -> None:
            """Assert that the level was never changed from the initial value.

            Raises:
                AssertionError: If the level was changed.
            """
            if len(self._history) > 1:
                history_names = [h[2] for h in self._history]
                msg = f"Expected level to not change, but history is: {history_names}"
                raise AssertionError(msg)

        def get_level_history(self) -> list[tuple[float, int, str]]:
            """Get the complete history of level changes.

            Returns:
                List of (timestamp, level_int, level_name) tuples.
            """
            return self._history.copy()

        def reset_to_initial(self) -> None:
            """Reset the root logger back to its initial level."""
            apathetic_logging.setRootLevel(self._initial_level_int)

    class LoggingIsolation:
        """Helper object for the isolated_logging fixture.

        Provides utilities for managing logger state during a test.
        """

        def __init__(
            self, saved_state: ApatheticTest_Internal_Logging.LoggingState
        ) -> None:
            """Initialize with saved state.

            Args:
                saved_state: The logging state that was saved before the test.
            """
            self._saved_state = saved_state

        def assert_root_level(self, expected: str | int) -> None:
            """Assert that the root logger has the expected level.

            Args:
                expected: The expected log level (string or int).

            Raises:
                AssertionError: If the levels don't match.
            """
            root = apathetic_logging.getRootLogger()
            expected_int = (
                apathetic_logging.getLevelNumber(expected)
                if isinstance(expected, str)
                else expected
            )
            actual = root.level

            if actual != expected_int:
                expected_name = apathetic_logging.getLevelNameStr(expected_int)
                actual_name = apathetic_logging.getLevelNameStr(actual)
                msg = (
                    f"Expected root logger level {expected_name} "
                    f"({expected_int}), but got {actual_name} ({actual})"
                )
                raise AssertionError(msg)

        def assert_logger_level(self, name: str, expected: str | int) -> None:
            """Assert that a logger has the expected level.

            Args:
                name: The logger name.
                expected: The expected log level (string or int).

            Raises:
                AssertionError: If the levels don't match or logger not found.
            """
            # Want logging.Logger so no apathetic_logging.getLogger
            logger = logging.getLogger(name)
            expected_int = (
                apathetic_logging.getLevelNumber(expected)
                if isinstance(expected, str)
                else expected
            )
            actual = logger.level

            if actual != expected_int:
                expected_name = apathetic_logging.getLevelNameStr(expected_int)
                actual_name = apathetic_logging.getLevelNameStr(actual)
                msg = (
                    f"Expected logger '{name}' level {expected_name} "
                    f"({expected_int}), but got {actual_name} ({actual})"
                )
                raise AssertionError(msg)

        def capture_streams(
            self,
        ) -> ApatheticTest_Private_Fixtures.StreamCapture:
            """Create a stream capture context manager for this test.

            Returns a context manager that captures stdout/stderr during
            logging. This is useful for tests that need to count log message
            occurrences, particularly duplication detection tests.

            Works reliably across all runtime modes (package, stitched,
            zipapp) and execution modes (serial, parallel with xdist).

            Returns:
                StreamCapture: Context manager for capturing output.

            Example:
                def test_no_duplication(isolated_logging):
                    with isolated_logging.capture_streams() as capture:
                        logger.debug("test message")
                        count = capture.count_message("test message")
                        assert count == 1
            """
            return ApatheticTest_Private_Fixtures.StreamCapture()


# ============================================================================
# Private Implementation Classes
# ============================================================================


class ApatheticTest_Private_Fixtures:  # noqa: N801
    """Container for private fixture implementation classes."""

    class LogRecordCapture(logging.Handler):
        """Internal handler that captures log records for message counting."""

        def __init__(self) -> None:
            super().__init__()
            self.records: list[logging.LogRecord] = []

        def emit(self, record: logging.LogRecord) -> None:
            """Store the log record."""
            self.records.append(record)

    class StreamCapture:
        """Context manager for capturing log messages to detect log duplication.

        Works reliably in xdist parallel mode, stitched mode, and all runtime
        modes. Alternative to pytest's caplog that avoids worker process
        inconsistencies.

        This is useful for tests that need to count occurrences of log
        messages, particularly duplication detection tests that may fail with
        pytest's caplog fixture in parallel mode or stitched mode.

        Uses logging record capture instead of stream redirection to work
        properly with apathetic-logging's handler system.

        Usage:
            def test_no_duplication(isolatedLogging):
                with isolatedLogging.captureStreams() as capture:
                    logger.debug("test message")
                    count = capture.count_message("test message")
                    assert count == 1
        """

        def __init__(self) -> None:
            self._capture_handler = ApatheticTest_Private_Fixtures.LogRecordCapture()
            self._capture_handler.setLevel(logging.DEBUG)

        def __enter__(self) -> Self:
            # Add our record capture handler to root logger
            root_logger = apathetic_logging.getRootLogger()
            root_logger.addHandler(self._capture_handler)
            return self

        def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: types.TracebackType | None,
        ) -> Literal[False]:
            # Remove our record capture handler
            root_logger = apathetic_logging.getRootLogger()
            root_logger.removeHandler(self._capture_handler)
            return False

        def count_message(self, message: str) -> int:
            """Count how many times a message appears in captured log records.

            Args:
                message: The message string to search for (case-sensitive
                    exact match).

            Returns:
                Number of times the exact message appears in records.
            """
            count = 0
            for record in self._capture_handler.records:
                if record.getMessage() == message:
                    count += 1
            return count


# ============================================================================
# Pytest Fixtures
# ============================================================================


@pytest.fixture
def atest_isolated_logging() -> Generator[
    ApatheticTest_Internal_Fixtures.LoggingIsolation, None, None
]:
    """Fixture providing complete test isolation for logging.

    This fixture saves the complete logging state before the test, clears
    all loggers and resets to defaults, and then restores the saved state
    after the test. This ensures that:

    - Logger class is reset
    - Registry data is reset
    - All loggers are removed
    - Root logger state is reset
    - No state bleeding between tests

    Yields:
        LoggingIsolation: Helper object with methods to manage logger state.

    Example:
        def test_logger_isolation(isolated_logging):
            apathetic_logging.setRootLevel("DEBUG")
            assert (
                apathetic_logging.getRootLogger().level
                == logging.DEBUG
            )

        def test_no_state_bleeding(isolated_logging):
            # Previous test's state is not present here
            root = apathetic_logging.getRootLogger()
            assert root.level != logging.DEBUG
    """
    _logging = ApatheticTest_Internal_Logging

    # Save state
    saved_state = _logging.save_logging_state()

    # Clear all loggers
    _logging.clear_all_loggers()

    # Reset to defaults (via apathetic_logging's defaults)
    try:
        apathetic_logging.Logger.extendLoggingModule()
    except (AttributeError, TypeError):
        # In case apathetic_logging is not fully initialized
        logging.setLoggerClass(logging.Logger)

    # Explicitly reset root logger to TEST level (matching test environment default)
    root = apathetic_logging.getRootLogger()
    root.setLevel(apathetic_logging.TEST_LEVEL)

    # Create and yield helper
    isolation = ApatheticTest_Internal_Fixtures.LoggingIsolation(saved_state)
    yield isolation

    # Cleanup: Remove all loggers again
    _logging.clear_all_loggers()

    # Restore state
    _logging.restore_logging_state(saved_state)


@pytest.fixture
def atest_logging_test_level(
    atest_isolated_logging: ApatheticTest_Internal_Fixtures.LoggingIsolation,
    monkeypatch: pytest.MonkeyPatch,
) -> ApatheticTest_Internal_Fixtures.LoggingTestLevel:
    """Fixture that sets root logger to TEST level and prevents downgrades.

    Use this fixture when you want your tests to default to maximum verbosity
    (TEST level) so you can see all debug logs if tests fail. The fixture
    prevents the app from downgrading the log level below TEST, ensuring
    debugging logs are always available.

    Yields:
        LoggingTestLevel: Helper with methods to control the prevention.

    Example:
        def test_with_verbose_logs(atest_logging_test_level):
            # Root logger is at TEST level
            app.initialize()  # App calls setRootLevel("INFO"), but it's ignored
            app.run()  # All logs visible because level stays at TEST

        def test_allow_app_to_change(atest_logging_test_level):
            # Sometimes you need to let the app change levels
            with atest_logging_test_level.temporarily_allow_changes():
                app.configure_logging(level="WARNING")
            # Level is now WARNING, but prevention re-enabled

    Note:
        The "TEST" level is 2 (DEBUG - 8), which is the most verbose level
        and bypasses pytest's capsys to write directly to sys.__stderr__.
        This allows you to see all output even if other tests capture output.
    """
    return ApatheticTest_Internal_Fixtures.LoggingTestLevel(
        atest_isolated_logging, monkeypatch
    )


@pytest.fixture
def atest_logging_level_testing(
    atest_isolated_logging: ApatheticTest_Internal_Fixtures.LoggingIsolation,
    request: pytest.FixtureRequest,
    monkeypatch: pytest.MonkeyPatch,
) -> ApatheticTest_Internal_Fixtures.LoggingLevelTesting:
    """Fixture for testing that your app correctly changes log levels.

    Use this when you want to test that your app's log level configuration
    works correctly (e.g., testing a CLI app's --log-level argument).

    The fixture sets a baseline log level, tracks all changes to the root
    logger level, and provides assertions to verify the changes.

    You can set the initial level via a pytest mark:

        @pytest.mark.initial_level("ERROR")
        def test_cli_sets_debug(atest_logging_level_testing):
            cli.main(["--log-level", "debug"])
            atest_logging_level_testing.assert_level_changed_from("ERROR", to="DEBUG")

    If no mark is provided, the default initial level is "ERROR" (quiet).

    Yields:
        LoggingLevelTesting: Helper with assertion methods.

    Example:
        @pytest.mark.initial_level("WARNING")
        def test_quiet_flag(atest_logging_level_testing):
            # Starts at WARNING
            atest_logging_level_testing.assert_root_level("WARNING")

            cli.main(["--quiet"])

            # Verify changed to ERROR or higher
            atest_logging_level_testing.assert_root_level("ERROR")

        @pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING", "ERROR"])
        def test_all_levels(atest_logging_level_testing, level):
            cli.main(["--log-level", level.lower()])
            atest_logging_level_testing.assert_root_level(level)
    """
    # Extract initial level from pytest mark if provided
    marker = request.node.get_closest_marker("initial_level")  # pyright: ignore[reportUnknownVariableType,reportUnknownMemberType]
    initial_level = marker.args[0] if marker else "ERROR"  # pyright: ignore[reportUnknownVariableType,reportUnknownMemberType,reportOptionalSubscript]  # Default to quiet

    return ApatheticTest_Internal_Fixtures.LoggingLevelTesting(
        atest_isolated_logging,
        initial_level,  # pyright: ignore[reportUnknownArgumentType]
        monkeypatch,
    )


@pytest.fixture
def atest_apathetic_logger() -> apathetic_logging.Logger:
    """Fixture providing a test logger with a unique name.

    This fixture creates a new logger with a unique name and sets it to
    TEST level (most verbose). It's useful for testing logger methods
    in isolation.

    Yields:
        Logger: A freshly created logger with a unique name.

    Example:
        def test_logger_methods(apathetic_logger):
            apathetic_logger.debug("This is visible")
            apathetic_logger.trace("So is this")
            assert apathetic_logger.levelName == "TEST"
    """
    logger = apathetic_logging.getLogger(f"test_logger_{uuid.uuid4().hex[:6]}")
    logger.setLevel(apathetic_logging.TEST_LEVEL)
    return logger


@pytest.fixture(autouse=True)
def atest_reset_logger_level() -> Generator[None, None, None]:
    """Reset logger level to TEST level before each test for consistency.

    In stitched mode, the logger is a module-level singleton that persists
    between tests. This fixture ensures the logger level is reset to TEST
    (the test environment default) before each test, preventing test
    interference and ensuring consistent logging behavior.

    This fixture is automatically used by all tests when the
    pytest_apathetic_logging plugin is loaded.
    """
    # Get the app logger and reset to TEST level
    logger = apathetic_logging.getRootLogger()
    # Reset to TEST level - this ensures tests start with a known state
    logger.setLevel(apathetic_logging.TEST_LEVEL)
    yield
    # After test, reset again to ensure clean state for next test
    logger.setLevel(apathetic_logging.TEST_LEVEL)


__all__ = [
    "ApatheticTest_Internal_Fixtures",
    "atest_apathetic_logger",
    "atest_isolated_logging",
    "atest_logging_level_testing",
    "atest_logging_test_level",
    "atest_reset_logger_level",
]
