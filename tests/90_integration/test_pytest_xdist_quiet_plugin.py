"""Integration test for pytest_xdist_quiet plugin.

This test verifies that the pytest_xdist_quiet plugin correctly suppresses
the benchmark warning when both xdist and pytest-benchmark plugins are active.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest_xdist_quiet.plugin as mod_plugin


def test_xdist_quiet_adds_filter_when_both_plugins_active() -> None:
    """Verify that xdist_quiet plugin adds filter when both plugins are active.

    The plugin should only add the filter warning when BOTH xdist and
    pytest-benchmark plugins are active in the config.
    """
    # --- setup ---
    # Create a mock config object
    mock_config = MagicMock()

    # Mock the hook attributes to indicate both plugins are active
    mock_hook = MagicMock()
    mock_hook.pytest_xdist_worker = MagicMock()  # xdist plugin is active
    mock_hook.pytest_benchmark_scale_unit = MagicMock()  # benchmark plugin active
    mock_config.pluginmanager.hook = mock_hook

    # Mock the getini to return empty filterwarnings initially
    mock_config.getini.return_value = []

    # --- execute ---
    # Call the pytest_configure hook
    mod_plugin.pytest_configure(mock_config)

    # --- verify ---
    # Verify that addinivalue_line was called with the correct filter
    xdist_filter = "ignore::pytest_benchmark.logger.PytestBenchmarkWarning"
    mock_config.addinivalue_line.assert_called_once_with("filterwarnings", xdist_filter)


def test_xdist_quiet_always_adds_filter() -> None:
    """Verify that xdist_quiet plugin always adds filter as a sane default.

    The plugin adds the filter regardless of which plugins are active,
    serving as a sane default that works out of the box.
    """
    # --- setup ---
    mock_config = MagicMock()
    mock_hook = MagicMock()
    mock_config.pluginmanager.hook = mock_hook

    # Mock the getini to return empty filterwarnings initially
    mock_config.getini.return_value = []

    # --- execute ---
    mod_plugin.pytest_configure(mock_config)

    # --- verify ---
    # Verify that addinivalue_line was called to add the filter
    xdist_filter = "ignore::pytest_benchmark.logger.PytestBenchmarkWarning"
    mock_config.addinivalue_line.assert_called_once_with("filterwarnings", xdist_filter)


def test_xdist_quiet_skips_if_filter_already_present() -> None:
    """Verify that xdist_quiet plugin skips adding filter if already present.

    The plugin should not add a duplicate filter if it's already configured.
    """
    # --- setup ---
    mock_config = MagicMock()

    # Mock the hook to indicate both plugins are active
    mock_hook = MagicMock()
    mock_hook.pytest_xdist_worker = MagicMock()
    mock_hook.pytest_benchmark_scale_unit = MagicMock()
    mock_config.pluginmanager.hook = mock_hook

    # Mock getini to return the filter already present
    xdist_filter = "ignore::pytest_benchmark.logger.PytestBenchmarkWarning"
    mock_config.getini.return_value = [xdist_filter]

    # --- execute ---
    mod_plugin.pytest_configure(mock_config)

    # --- verify ---
    # Verify that addinivalue_line was NOT called (filter already present)
    mock_config.addinivalue_line.assert_not_called()
