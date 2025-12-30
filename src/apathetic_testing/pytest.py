"""Pytest detection utilities.

This module provides utilities for detecting if code is running under pytest.
"""

from __future__ import annotations

import os
import sys


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


__all__ = [
    "ApatheticTest_Internal_Pytest",
]
