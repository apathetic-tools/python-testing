"""Logging utilities for state management and assertions in tests.

This module provides the core logging state management functionality used by
the pytest fixtures in the fixtures module. It includes utilities for saving,
restoring, and asserting logger state.

For pytest fixtures and test integration, see the fixtures module:
- atest_isolated_logging: Complete test isolation
- atest_logging_test_level: TEST level with downgrade prevention
- atest_logging_level_testing: Track and verify level changes
- atest_apathetic_logger: Per-test unique logger
"""

from __future__ import annotations

import logging
import sys
from dataclasses import dataclass
from typing import Any

import apathetic_logging

from apathetic_testing.constants import ApatheticTest_Internal_Constants


# ============================================================================
# Logging Mixin
# ============================================================================


class ApatheticTest_Internal_Logging:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class providing logging-related utilities."""

    @dataclass(frozen=True)
    class RootLoggerState:
        """Snapshot of root logger state."""

        level: int
        """The explicit log level set on the root logger."""

        handlers: list[logging.Handler]
        """List of handlers attached to the root logger."""

        propagate: bool
        """Whether the root logger propagates to parent (always False for root)."""

        disabled: bool
        """Disabled state of the root logger."""

        filters: list[logging.Filter]
        """List of filters attached to the root logger."""

    @dataclass(frozen=True)
    class LoggingState:
        """Complete snapshot of logging state for save/restore."""

        logger_class: type[logging.Logger]
        """The registered logger class."""

        registry_data: dict[str, Any]
        """Registry data (8 configurable fields)."""

        root_logger_user_configured: bool | None
        """Value of _root_logger_user_configured flag."""

        logger_dict: dict[str, logging.Logger | logging.PlaceHolder]
        """Copy of logging.Logger.manager.loggerDict."""

        root_logger_state: ApatheticTest_Internal_Logging.RootLoggerState
        """Snapshot of root logger's state."""

    @staticmethod
    def assert_level_equals(
        logger: logging.Logger,
        expected: str | int,
        *,
        effective: bool = True,
    ) -> None:
        """Assert that a logger has the expected level.

        Args:
            logger: The logger to check.
            expected: The expected level (string or int).
            effective: If True, check effective (inherited) level;
                if False, check explicit level.

        Raises:
            AssertionError: If the levels don't match.
        """
        expected_int = (
            apathetic_logging.getLevelNumber(expected)
            if isinstance(expected, str)
            else expected
        )

        actual = logger.getEffectiveLevel() if effective else logger.level

        if actual != expected_int:
            expected_name = apathetic_logging.getLevelNameStr(expected_int)
            actual_name = apathetic_logging.getLevelNameStr(actual)
            msg = (
                f"Expected logger level {expected_name} ({expected_int}), "
                f"but got {actual_name} ({actual})"
            )
            raise AssertionError(msg)

    @staticmethod
    def assert_root_level_equals(
        expected: str | int,
    ) -> None:
        """Assert that the root logger has the expected level.

        Args:
            expected: The expected level (string or int).

        Raises:
            AssertionError: If the levels don't match.
        """
        _constants = ApatheticTest_Internal_Constants
        _logging = ApatheticTest_Internal_Logging
        root = logging.getLogger(_constants.ROOT_LOGGER_KEY)
        _logging.assert_level_equals(root, expected, effective=False)

    @staticmethod
    def assert_handler_count(
        logger: logging.Logger,
        expected: int,
        *,
        handler_type: type[logging.Handler] | None = None,
    ) -> None:
        """Assert that a logger has the expected number of handlers.

        Args:
            logger: The logger to check.
            expected: The expected number of handlers.
            handler_type: If provided, only count handlers of this type.

        Raises:
            AssertionError: If the count doesn't match.
        """
        handlers = logger.handlers
        if handler_type:
            handlers = [h for h in handlers if isinstance(h, handler_type)]

        actual = len(handlers)
        if actual != expected:
            type_str = f" of type {handler_type.__name__}" if handler_type else ""
            msg = (
                f"Expected logger to have {expected} handler(s){type_str}, "
                f"but got {actual}"
            )
            raise AssertionError(msg)

    @staticmethod
    def save_logging_state() -> ApatheticTest_Internal_Logging.LoggingState:
        """Save the complete logging state.

        This saves everything needed to restore logging to its current state,
        including logger class, registry data, user configuration flags, all
        loggers in the registry, and the root logger's state.

        Returns:
            LoggingState: A snapshot of the current logging state.
        """
        _constants = ApatheticTest_Internal_Constants
        _logging = ApatheticTest_Internal_Logging

        # Save logger class
        logger_class = logging.getLoggerClass()

        # Save registry data (8 fields)
        # In package mode: module exports the class via __init__.py
        # In stitched mode: the class is available directly
        registry: Any = (
            apathetic_logging.apathetic_logging
            if hasattr(apathetic_logging, "apathetic_logging")
            else apathetic_logging
        )
        registry_data = {
            "registered_internal_logger_name": (
                registry.registered_internal_logger_name
            ),
            "registered_internal_default_log_level": (
                registry.registered_internal_default_log_level
            ),
            "registered_internal_log_level_env_vars": (
                registry.registered_internal_log_level_env_vars
            ),
            "registered_internal_compatibility_mode": (
                registry.registered_internal_compatibility_mode
            ),
            "registered_internal_propagate": (registry.registered_internal_propagate),
            "registered_internal_replace_root_logger": (
                registry.registered_internal_replace_root_logger
            ),
            "registered_internal_port_handlers": (
                registry.registered_internal_port_handlers
            ),
            "registered_internal_port_level": (registry.registered_internal_port_level),
        }

        # Save _root_logger_user_configured flag
        logger_module = sys.modules.get("apathetic_logging.logger")
        root_logger_user_configured = (
            getattr(logger_module, "_root_logger_user_configured", None)
            if logger_module
            else None
        )

        # Save logger dict (copy the dict, not the loggers themselves)
        logger_dict = logging.Logger.manager.loggerDict.copy()

        # Save root logger state
        root = logging.getLogger(_constants.ROOT_LOGGER_KEY)
        root_logger_state = _logging.RootLoggerState(
            level=root.level,
            handlers=root.handlers.copy(),
            propagate=root.propagate,
            disabled=root.disabled,
            filters=[f for f in root.filters if isinstance(f, logging.Filter)],
        )

        return _logging.LoggingState(
            logger_class=logger_class,
            registry_data=registry_data,
            root_logger_user_configured=root_logger_user_configured,
            logger_dict=logger_dict,
            root_logger_state=root_logger_state,
        )

    @staticmethod
    def restore_logging_state(
        state: ApatheticTest_Internal_Logging.LoggingState,
    ) -> None:
        """Restore logging to a previously saved state.

        Args:
            state: The LoggingState to restore from.
        """
        _constants = ApatheticTest_Internal_Constants

        # Restore logger class
        logging.setLoggerClass(state.logger_class)

        # Restore registry data
        # In package mode: module exports the class via __init__.py
        # In stitched mode: the class is available directly
        registry: Any = (
            apathetic_logging.apathetic_logging
            if hasattr(apathetic_logging, "apathetic_logging")
            else apathetic_logging
        )
        registry.registered_internal_logger_name = state.registry_data[
            "registered_internal_logger_name"
        ]
        registry.registered_internal_default_log_level = state.registry_data[
            "registered_internal_default_log_level"
        ]
        registry.registered_internal_log_level_env_vars = state.registry_data[
            "registered_internal_log_level_env_vars"
        ]
        registry.registered_internal_compatibility_mode = state.registry_data[
            "registered_internal_compatibility_mode"
        ]
        registry.registered_internal_propagate = state.registry_data[
            "registered_internal_propagate"
        ]
        registry.registered_internal_replace_root_logger = state.registry_data[
            "registered_internal_replace_root_logger"
        ]
        registry.registered_internal_port_handlers = state.registry_data[
            "registered_internal_port_handlers"
        ]
        registry.registered_internal_port_level = state.registry_data[
            "registered_internal_port_level"
        ]

        # Restore _root_logger_user_configured flag
        logger_module = sys.modules.get("apathetic_logging.logger")
        if logger_module:
            if state.root_logger_user_configured is None:
                if hasattr(logger_module, "_root_logger_user_configured"):
                    delattr(logger_module, "_root_logger_user_configured")
            else:
                logger_module._root_logger_user_configured = (  # type: ignore[attr-defined]  # noqa: SLF001
                    state.root_logger_user_configured
                )

        # Restore logger dict (remove all current, restore from saved)
        current_names = list(logging.Logger.manager.loggerDict.keys())
        for name in current_names:
            logging.Logger.manager.loggerDict.pop(name, None)

        for name, logger in state.logger_dict.items():
            logging.Logger.manager.loggerDict[name] = logger

        # Restore root logger state
        root = logging.getLogger(_constants.ROOT_LOGGER_KEY)
        root.setLevel(state.root_logger_state.level)
        root.propagate = state.root_logger_state.propagate
        root.disabled = state.root_logger_state.disabled

        # Clear current handlers
        root.handlers.clear()

        # Restore handlers
        for handler in state.root_logger_state.handlers:
            root.addHandler(handler)

        # Restore filters
        if hasattr(root, "filters"):
            root.filters.clear()
            for filt in state.root_logger_state.filters:
                root.addFilter(filt)

    @staticmethod
    def clear_all_loggers() -> None:
        """Remove all loggers from the logging registry except the root logger.

        This is useful for test cleanup to ensure a clean state for the next test.
        """
        logger_names = list(logging.Logger.manager.loggerDict.keys())
        for name in logger_names:
            if name not in {"root", ""}:
                logging.Logger.manager.loggerDict.pop(name, None)


__all__ = [
    "ApatheticTest_Internal_Logging",
]
