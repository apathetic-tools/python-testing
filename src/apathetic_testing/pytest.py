"""Pytest detection utilities.

This module provides utilities for detecting if code is running under pytest
and for checking pytest configuration options.
"""

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    import pytest


# ============================================================================
# Pytest Mixin
# ============================================================================


class ApatheticTest_Internal_Pytest:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class providing pytest-related utilities."""

    @staticmethod
    def is_running_under_pytest() -> bool:
        """Detect if code is running under pytest.

        Checks multiple indicators:
        - Environment variables set by pytest
        - Command-line arguments containing 'pytest'

        Returns:
            True if running under pytest, False otherwise
        """
        return (
            "pytest" in os.environ.get("_", "")
            or "PYTEST_CURRENT_TEST" in os.environ
            or any(
                "pytest" in arg
                for arg in sys.argv
                if isinstance(arg, str)  # pyright: ignore[reportUnnecessaryIsInstance]
            )
        )

    @staticmethod
    def has_pytest_user_config(config: pytest.Config, option_name: str) -> bool:
        """Check if a pytest option has been configured by the user.

        Checks all configuration sources in order:
        1. pytest.ini / pyproject.toml
        2. Environment variables (for timeout: PYTEST_TIMEOUT)
        3. CLI flags (--<option-name>)

        Args:
            config: The pytest Config object
            option_name: Name of the option to check (e.g., 'timeout')

        Returns:
            True if the user has configured this option via any method,
            False otherwise
        """
        # Check config file and environment variables
        try:
            config_value = config.getini(option_name)
            if config_value:
                return True
        except (KeyError, ValueError):
            pass

        # Check CLI flag
        try:
            cli_value = config.getoption(option_name)
            if cli_value:
                return True
        except (ValueError, AttributeError):
            pass

        return False

    @staticmethod
    def has_pytest_plugin_enabled(
        config: pytest.Config, plugin_names: str | list[str]
    ) -> bool:
        """Check if all specified pytest plugins are enabled.

        Checks if the given plugin(s) are actually enabled (not disabled via
        -p no:pluginname flag). Uses config.pluginmanager.hasplugin() which
        respects the -p no:pluginname flag.

        Args:
            config: The pytest Config object
            plugin_names: A single plugin name (str) or list of plugin names to
                check (e.g., 'benchmark', 'xdist').

        Returns:
            True if all specified plugins are enabled, False otherwise
        """
        # Normalize to list
        if isinstance(plugin_names, str):
            plugin_names = [plugin_names]

        # Check if all requested plugins are enabled using hasplugin(),
        # which respects -p no:pluginname flags
        return all(config.pluginmanager.hasplugin(plugin) for plugin in plugin_names)


__all__ = [
    "ApatheticTest_Internal_Pytest",
]
