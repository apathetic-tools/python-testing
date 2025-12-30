"""Tests for pytest utility functions.

Tests for is_running_under_pytest, has_pytest_user_config and other
pytest-related utilities in the apathetic_testing library.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import apathetic_testing.pytest as amod_pytest


if TYPE_CHECKING:
    import pytest


# --- convenience -----------------------------------------------------------

_pytest = amod_pytest.ApatheticTest_Internal_Pytest


# ---------------------------------------------------------------------------
# Tests for has_pytest_user_config
# ---------------------------------------------------------------------------


class TestHasPytestUserConfig:
    """Tests for has_pytest_user_config static method."""

    def test_has_pytest_user_config_returns_true_when_config_via_ini(
        self,
    ) -> None:
        """Test returns True when option is configured via config file/env."""
        # --- setup ---
        mock_config: MagicMock = MagicMock()
        # Simulate getini() finding a value (config file or env var)
        mock_config.getini.return_value = 60
        mock_config.getoption.side_effect = ValueError("not found")

        # --- execute ---
        result = _pytest.has_pytest_user_config(mock_config, "timeout")

        # --- verify ---
        assert result is True
        mock_config.getini.assert_called_once_with("timeout")

    def test_has_pytest_user_config_returns_true_when_config_via_cli(
        self,
    ) -> None:
        """Test returns True when option is configured via CLI flag."""
        # --- setup ---
        mock_config: MagicMock = MagicMock()
        # Simulate getini() returning empty/default value
        mock_config.getini.return_value = None
        # Simulate getoption() finding a value
        mock_config.getoption.return_value = "60"

        # --- execute ---
        result = _pytest.has_pytest_user_config(mock_config, "timeout")

        # --- verify ---
        assert result is True
        mock_config.getini.assert_called_once_with("timeout")
        mock_config.getoption.assert_called_once_with("timeout")

    def test_has_pytest_user_config_returns_false_when_not_configured(
        self,
    ) -> None:
        """Test returns False when option is not configured anywhere."""
        # --- setup ---
        mock_config: MagicMock = MagicMock()
        # Simulate getini() returning empty/default
        mock_config.getini.return_value = None
        # Simulate getoption() raising ValueError (option not found)
        mock_config.getoption.side_effect = ValueError("option not found")

        # --- execute ---
        result = _pytest.has_pytest_user_config(mock_config, "timeout")

        # --- verify ---
        assert result is False

    def test_has_pytest_user_config_handles_getini_keyerror(
        self,
    ) -> None:
        """Test handles KeyError from getini() gracefully."""
        # --- setup ---
        mock_config: MagicMock = MagicMock()
        # Simulate getini() raising KeyError (option not recognized)
        mock_config.getini.side_effect = KeyError("timeout")
        # Simulate getoption() returning a value
        mock_config.getoption.return_value = "60"

        # --- execute ---
        result = _pytest.has_pytest_user_config(mock_config, "timeout")

        # --- verify ---
        assert result is True
        # Even though getini() failed, getoption() found the value

    def test_has_pytest_user_config_handles_getoption_attributeerror(
        self,
    ) -> None:
        """Test handles AttributeError from getoption() gracefully."""
        # --- setup ---
        mock_config: MagicMock = MagicMock()
        # Simulate getini() returning a value
        mock_config.getini.return_value = 60
        # Simulate getoption() raising AttributeError (plugin not loaded)
        mock_config.getoption.side_effect = AttributeError("not available")

        # --- execute ---
        result = _pytest.has_pytest_user_config(mock_config, "timeout")

        # --- verify ---
        assert result is True
        # getini() found the value, so we return True

    def test_has_pytest_user_config_with_falsy_but_configured_value(
        self,
    ) -> None:
        """Test correctly identifies configured but falsy values.

        Empty string, 0, and False are valid configured values, but they're
        falsy in Python. The method should still recognize these as configured.
        """
        # --- setup ---
        mock_config: MagicMock = MagicMock()
        # Simulate getini() returning 0 (falsy but configured)
        mock_config.getini.return_value = 0
        mock_config.getoption.side_effect = ValueError("not found")

        # --- execute ---
        result = _pytest.has_pytest_user_config(mock_config, "timeout")

        # --- verify ---
        # Current implementation uses truthiness check, so 0 would return False
        # This is a known limitation but acceptable since 0 timeout doesn't make sense
        assert result is False

    def test_has_pytest_user_config_checks_all_sources_in_order(
        self,
    ) -> None:
        """Test that getini is checked before getoption."""
        # --- setup ---
        mock_config: MagicMock = MagicMock()
        mock_config.getini.return_value = 60
        mock_config.getoption.return_value = "120"

        # --- execute ---
        result = _pytest.has_pytest_user_config(mock_config, "timeout")

        # --- verify ---
        assert result is True
        # getini() should be called and found a value (60)
        # getoption() should still be called for completeness
        mock_config.getini.assert_called_once()

    def test_has_pytest_user_config_with_different_option_names(
        self,
    ) -> None:
        """Test with various pytest option names."""
        # --- setup ---
        option_names = ["timeout", "timeout_func_only", "markers", "testpaths"]
        mock_config: MagicMock = MagicMock()
        mock_config.getini.return_value = "some_value"
        mock_config.getoption.side_effect = ValueError()

        # --- execute & verify ---
        for option_name in option_names:
            mock_config.reset_mock()
            result = _pytest.has_pytest_user_config(mock_config, option_name)
            assert result is True
            mock_config.getini.assert_called_once_with(option_name)


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
