# tests/30_independant/test_is_running_under_pytest.py
"""Tests for is_running_under_pytest function.

Tests for is_running_under_pytest, including detection via environment
variables, pytest current test marker, and CLI arguments.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import apathetic_testing.pytest as amod_pytest


if TYPE_CHECKING:
    import pytest


# --- convenience -----------------------------------------------------------

_pytest = amod_pytest.ApatheticTest_Internal_Pytest


# ---------------------------------------------------------------------------
# Tests for is_running_under_pytest
# ---------------------------------------------------------------------------


class TestIsRunningUnderPytest:
    """Tests for is_running_under_pytest static method."""

    def test_is_running_under_pytest_in_current_environment(
        self,
    ) -> None:
        """Test that is_running_under_pytest returns True when run via pytest."""
        # --- execute ---
        # This test is running under pytest, so it should return True
        result = _pytest.is_running_under_pytest()

        # --- verify ---
        assert result is True

    def test_is_running_under_pytest_detects_pytest_in_underscore_env(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test detection via '_' environment variable."""
        # --- setup ---
        monkeypatch.setenv("_", "/usr/local/bin/pytest")
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

        # --- execute ---
        result = _pytest.is_running_under_pytest()

        # --- verify ---
        assert result is True

    def test_is_running_under_pytest_detects_pytest_current_test_env(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test detection via PYTEST_CURRENT_TEST environment variable."""
        # --- setup ---
        monkeypatch.setenv("PYTEST_CURRENT_TEST", "test_file.py::test_func")
        monkeypatch.setenv("_", "")

        # --- execute ---
        result = _pytest.is_running_under_pytest()

        # --- verify ---
        assert result is True

    def test_is_running_under_pytest_returns_false_without_indicators(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test returns False when no pytest indicators are present."""
        # --- setup ---
        monkeypatch.setenv("_", "/usr/bin/python")
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
        # Mock sys.argv to not contain pytest
        monkeypatch.setattr(
            "sys.argv",
            ["python", "script.py"],
        )

        # --- execute ---
        result = _pytest.is_running_under_pytest()

        # --- verify ---
        assert result is False
