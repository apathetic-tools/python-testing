"""Pytest plugin for quiet mode output suppression."""

from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest options based on verbosity.

    In quiet mode (verbose <= 0), modifies reportchars to exclude skipped tests
    for cleaner output. The -ra flag in pytest.ini shows all, but quiet mode
    hides skipped and passed output.
    """
    verbose = getattr(config.option, "verbose", 0)
    if verbose <= 0:
        # In quiet mode, modify reportchars to exclude skipped tests ('s')
        reportchars = getattr(config.option, "reportchars", "")
        if reportchars == "a":
            # 'a' means "all except passed", change to exclude skipped and passed
            # Use explicit chars: f (failed), E (error), x (xfailed), X (xpassed)
            config.option.reportchars = "fExX"
        elif "s" in reportchars or "P" in reportchars:
            # Remove 's' (skipped) and 'P' (passed with output) in quiet mode
            config.option.reportchars = reportchars.replace("s", "").replace("P", "")


__all__ = ["pytest_configure"]
