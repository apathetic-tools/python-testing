"""Pytest plugin for filtering debug-marked tests."""

from __future__ import annotations

import pytest


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """Filter debug-marked tests unless explicitly requested.

    Tests marked with @pytest.mark.debug are hidden from normal test runs.
    They are only included if the user explicitly filters for them using -k debug.
    """
    # Detect if the user is filtering for debug tests
    keywords = config.getoption("-k") or ""
    running_debug = "debug" in keywords.lower()

    if running_debug:
        return  # User explicitly requested them, don't skip

    for item in items:
        # Check for the actual @pytest.mark.debug marker, not just "debug" in keywords
        # (parametrized values can add "debug" to keywords, causing false positives)
        if item.get_closest_marker("debug") is not None:
            item.add_marker(
                pytest.mark.skip(reason="Skipped debug test (use -k debug to run)"),
            )


__all__ = ["pytest_collection_modifyitems"]
