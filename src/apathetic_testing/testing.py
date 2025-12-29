# src/apathetic_testing/testing.py
"""Test utilities mixin for reusable test helpers."""

from __future__ import annotations

from pathlib import Path


class ApatheticTest_Internal_Testing:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class providing reusable test utilities.

    Inherit from this mixin in your test classes to access shared test utilities
    that can be used across multiple projects.
    """

    @staticmethod
    def _short_path(path: str | None) -> str:
        """Return a shortened version of a path for logging."""
        if not path:
            return "n/a"
        # Use a simple approach: show last MAX_PATH_COMPONENTS or full path if shorter
        max_path_components = 3
        path_obj = Path(path)
        parts = path_obj.parts
        if len(parts) > max_path_components:
            return str(Path(*parts[-max_path_components:]))
        return path
