"""Pytest plugin for xdist-related warning suppression."""

from __future__ import annotations

from typing import TYPE_CHECKING

from apathetic_testing import has_pytest_plugin_enabled  # noqa: ICN003


if TYPE_CHECKING:
    import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Add filterwarnings to suppress pytest-benchmark warnings as a sane default.

    When running tests with xdist (parallel execution), pytest-benchmark
    automatically disables benchmarks and emits a warning. This is expected
    behavior and this filter suppresses it for cleaner output.

    This plugin serves as a sane default that automatically adds the filter
    without requiring manual pytest.ini configuration. It skips adding the filter
    if it's already configured to avoid duplicates.
    """
    if not has_pytest_plugin_enabled(config, ["xdist", "benchmark"]):
        return

    xdist_filter = "ignore::pytest_benchmark.logger.PytestBenchmarkWarning"

    # Check if the filter is already configured
    filterwarnings = config.getini("filterwarnings")
    if xdist_filter not in filterwarnings:
        # Use addinivalue_line to add the filterwarning
        config.addinivalue_line("filterwarnings", xdist_filter)


__all__ = ["pytest_configure"]
