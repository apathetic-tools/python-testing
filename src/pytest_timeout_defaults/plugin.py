"""Pytest plugin for default timeout configuration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from apathetic_testing import (  # noqa: ICN003
    has_pytest_plugin_enabled,
    has_pytest_user_config,
)


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
    if not has_pytest_plugin_enabled(config, "timeout"):
        return

    # Only apply defaults if user hasn't configured timeout via any method
    if not has_pytest_user_config(config, "timeout"):
        # Set default timeout to 60 seconds
        config.inicfg["timeout"] = 60

        # Only set timeout_func_only if user hasn't configured it
        if not has_pytest_user_config(config, "timeout_func_only"):
            # Only set to False when using our default timeout and user
            # hasn't configured this option
            config.inicfg["timeout_func_only"] = False


__all__ = ["pytest_configure"]
