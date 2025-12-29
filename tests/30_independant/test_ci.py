# tests/30_independant/test_ci.py
"""Tests for CI detection utilities."""

import pytest

import apathetic_testing as mod_autils


def test_is_ci_when_ci_env_var_set(monkeypatch: pytest.MonkeyPatch) -> None:
    """is_ci() should return True when CI environment variable is set."""
    # --- setup ---
    monkeypatch.setenv("CI", "true")

    # --- execute ---
    result = mod_autils.is_ci()

    # --- verify ---
    assert result is True


def test_is_ci_when_github_actions_set(monkeypatch: pytest.MonkeyPatch) -> None:
    """is_ci() should return True when GITHUB_ACTIONS is set."""
    # --- setup ---
    monkeypatch.setenv("GITHUB_ACTIONS", "true")

    # --- execute ---
    result = mod_autils.is_ci()

    # --- verify ---
    assert result is True


def test_is_ci_when_no_ci_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    """is_ci() should return False when no CI environment variables are set."""
    # --- setup ---
    # Remove all CI-related env vars
    for var in mod_autils.CI_ENV_VARS:
        monkeypatch.delenv(var, raising=False)

    # --- execute ---
    result = mod_autils.is_ci()

    # --- verify ---
    assert result is False


def test_if_ci_returns_ci_value_when_in_ci(monkeypatch: pytest.MonkeyPatch) -> None:
    """if_ci() should return ci_value when running in CI."""
    # --- setup ---
    monkeypatch.setenv("CI", "true")

    # --- execute ---
    result = mod_autils.if_ci("ci_value", "local_value")

    # --- verify ---
    assert result == "ci_value"


def test_if_ci_returns_local_value_when_not_in_ci(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """if_ci() should return local_value when not running in CI."""
    # --- setup ---
    # Remove all CI-related env vars
    for var in mod_autils.CI_ENV_VARS:
        monkeypatch.delenv(var, raising=False)

    # --- execute ---
    result = mod_autils.if_ci("ci_value", "local_value")

    # --- verify ---
    assert result == "local_value"


def test_if_ci_with_different_types(monkeypatch: pytest.MonkeyPatch) -> None:
    """if_ci() should work with different value types."""
    # --- setup ---
    monkeypatch.setenv("CI", "true")

    # --- execute and verify ---
    assert mod_autils.if_ci(100, 200) == 100  # noqa: PLR2004
    assert mod_autils.if_ci([1, 2], [3, 4]) == [1, 2]
    assert mod_autils.if_ci(True, False) is True

    # --- setup for local ---
    for var in mod_autils.CI_ENV_VARS:
        monkeypatch.delenv(var, raising=False)

    # --- execute and verify ---
    assert mod_autils.if_ci(100, 200) == 200  # noqa: PLR2004
    assert mod_autils.if_ci([1, 2], [3, 4]) == [3, 4]
    assert mod_autils.if_ci(True, False) is False


def test_is_ci_false_return_path(monkeypatch: pytest.MonkeyPatch) -> None:
    """is_ci() should return False when no CI vars are set (line 41)."""
    # This test ensures line 41 (False return path) is explicitly covered
    # --- setup ---
    # Ensure all CI env vars are unset
    for var in mod_autils.CI_ENV_VARS:
        monkeypatch.delenv(var, raising=False)

    # --- execute ---
    result = mod_autils.is_ci()

    # --- verify ---
    # Line 41: return bool(...) when no vars are set should return False
    assert result is False
    assert isinstance(result, bool)


def test_if_ci_local_value_return_path(monkeypatch: pytest.MonkeyPatch) -> None:
    """if_ci() should return local_value when not in CI (line 66)."""
    # This test ensures line 66 (local_value return path) is explicitly covered
    # --- setup ---
    # Ensure all CI env vars are unset
    for var in mod_autils.CI_ENV_VARS:
        monkeypatch.delenv(var, raising=False)

    # --- execute ---
    # Line 66: return ci_value if is_ci() else local_value
    # When is_ci() is False, should return local_value
    result = mod_autils.if_ci("should_not_return", "should_return_this")

    # --- verify ---
    assert result == "should_return_this"
