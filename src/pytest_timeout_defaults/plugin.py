"""Pytest plugin for default timeout configuration."""

from __future__ import annotations

from typing import TYPE_CHECKING

import apathetic_testing.pytest as ap_pytest


if TYPE_CHECKING:
    import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Set default timeout if not already configured by user.

    This plugin only sets the timeout to 60 seconds if the user hasn't
    already configured one. Users can override this via:
    - pytest.ini / pyproject.toml: timeout = <seconds>
    - Environment variable: PYTEST_TIMEOUT=<seconds>
    - CLI flag: --timeout=<seconds>

    When using the default timeout, timeout_func_only is also set to False
    to ensure all tests (not just functions) respect the timeout.
    """
    # Check if pytest-timeout plugin is active
    has_timeout_plugin = hasattr(config.pluginmanager.hook, "pytest_timeout")

    if not has_timeout_plugin:
        # pytest-timeout is not installed, skip configuration
        return

    # Check if timeout was configured via any method
    try:
        config.getini("timeout")
    except (KeyError, ValueError):
        # Option doesn't exist or can't be read, skip
        return

    # Only apply defaults if user hasn't configured timeout via any method
    user_configured_timeout = (
        ap_pytest.ApatheticTest_Internal_Pytest.has_pytest_user_config(
            config, "timeout"
        )
    )

    if (
        not user_configured_timeout
        and hasattr(config, "inicfg")
        and isinstance(config.inicfg, dict)
    ):
        # Set default timeout to 60 seconds
        config.inicfg["timeout"] = 60

        # Only set timeout_func_only if user hasn't configured it
        user_configured_func_only = (
            ap_pytest.ApatheticTest_Internal_Pytest.has_pytest_user_config(
                config, "timeout_func_only"
            )
        )

        if not user_configured_func_only:
            # Only set to False when using our default timeout and user
            # hasn't configured this option
            config.inicfg["timeout_func_only"] = False


__all__ = ["pytest_configure"]
