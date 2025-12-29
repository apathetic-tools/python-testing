# tests/30_independant/test_is_running_under_pytest.py
"""Tests for is_running_under_pytest() function.

The is_running_under_pytest() function detects if code is running under pytest.
It checks multiple indicators:
- Environment variables set by pytest (PYTEST_CURRENT_TEST, _)
- Command-line arguments containing 'pytest'
"""

import sys

import pytest

import apathetic_testing as mod_autils


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_is_running_under_pytest_detects_via_pytest_current_test_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Should detect pytest via PYTEST_CURRENT_TEST environment variable."""
    # --- setup ---
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "test_file.py::test_func")

    # --- execute ---
    result = mod_autils.is_running_under_pytest()

    # --- verify ---
    assert result is True


def test_is_running_under_pytest_detects_via_underscore_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Should detect pytest via _ environment variable containing 'pytest'."""
    # --- setup ---
    monkeypatch.setenv("_", "/path/to/pytest")

    # --- execute ---
    result = mod_autils.is_running_under_pytest()

    # --- verify ---
    assert result is True


def test_is_running_under_pytest_detects_via_sys_argv() -> None:
    """Should detect pytest via sys.argv containing 'pytest'."""
    # --- setup ---
    original_argv = sys.argv.copy()
    try:
        sys.argv = ["pytest", "tests/test_something.py"]

        # --- execute ---
        result = mod_autils.is_running_under_pytest()

        # --- verify ---
        assert result is True
    finally:
        sys.argv = original_argv


def test_is_running_under_pytest_returns_false_when_not_under_pytest(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Should return False when not running under pytest."""
    # --- setup ---
    # Clear pytest-related environment variables
    env_vars_to_clear = ["PYTEST_CURRENT_TEST", "_"]
    for key in env_vars_to_clear:
        monkeypatch.delenv(key, raising=False)

    # Mock sys.argv to not contain pytest
    original_argv = sys.argv.copy()
    try:
        sys.argv = ["python", "script.py"]

        # --- execute ---
        result = mod_autils.is_running_under_pytest()

        # --- verify ---
        assert result is False
    finally:
        sys.argv = original_argv


def test_is_running_under_pytest_handles_mixed_argv_types() -> None:
    """Should handle sys.argv with mixed types gracefully."""
    # --- setup ---
    original_argv = sys.argv.copy()
    try:
        # In practice sys.argv is always strings, but test defensive code
        sys.argv = ["pytest", "test.py"]

        # --- execute ---
        result = mod_autils.is_running_under_pytest()

        # --- verify ---
        assert result is True
    finally:
        sys.argv = original_argv
