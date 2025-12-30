"""Tests for patch_everywhere function.

Tests for patch_everywhere, including stitched mode isolation and respecting
stitch hints.
"""

from __future__ import annotations

from types import ModuleType
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import apathetic_testing as mod_apathetic_testing


if TYPE_CHECKING:
    import pytest


def test_patch_everywhere_stitched_mode_preserves_isolation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that patch_everywhere doesn't corrupt test isolation in stitched mode.

    This test simulates stitched build behavior where multiple functions
    share a single __globals__ dictionary. Running patch_everywhere multiple
    times should not corrupt the shared namespace.
    """
    # Create a mock stitched module with multiple functions sharing __globals__
    stitched_module = ModuleType("mock_stitched")
    stitched_module.__file__ = "/dist/mock_stitched.py"  # Stitched indicator

    # Define functions that will share the same __globals__
    def func_a() -> str:
        return "original_a"

    def func_b() -> str:
        return "original_b"

    # Add to the module (they'll share __globals__)
    stitched_module.func_a = func_a  # type: ignore[attr-defined]
    stitched_module.func_b = func_b  # type: ignore[attr-defined]

    # Verify they share __globals__ (stitched behavior)
    assert func_a.__globals__ is func_b.__globals__, (
        "Test setup: functions should share __globals__ in stitched mode"
    )

    # Simulate what happens in a test suite:
    # Test 1: Mock func_a
    mock_a1 = MagicMock(return_value="mock_a1")
    mod_apathetic_testing.patch_everywhere(
        monkeypatch,
        stitched_module,
        "func_a",
        mock_a1,
        package_prefix="mock_stitched",
        stitch_hints={"/dist/"},
    )

    # Call the function - should use mock
    result = stitched_module.func_a()
    assert result == "mock_a1", "First patch should be active"
    mock_a1.assert_called_once()

    # Test 2: Mock func_b (in a different test, cleanup happens between)
    # Simulate test teardown/setup cycle
    monkeypatch.undo()

    mock_b = MagicMock(return_value="mock_b")
    mod_apathetic_testing.patch_everywhere(
        monkeypatch,
        stitched_module,
        "func_b",
        mock_b,
        package_prefix="mock_stitched",
        stitch_hints={"/dist/"},
    )

    # Call func_b - should use mock
    result = stitched_module.func_b()
    assert result == "mock_b", "Second patch should work after first is undone"
    mock_b.assert_called_once()

    # Test 3: The problematic case - mock a function again
    # This previously would fail because __globals__ was corrupted
    monkeypatch.undo()

    mock_a2 = MagicMock(return_value="mock_a2")
    mod_apathetic_testing.patch_everywhere(
        monkeypatch,
        stitched_module,
        "func_a",
        mock_a2,
        package_prefix="mock_stitched",
        stitch_hints={"/dist/"},
    )

    # This is where it would fail in buggy code:
    # The mock wouldn't be called because __globals__ is corrupted
    result = stitched_module.func_a()
    assert result == "mock_a2", "Third patch (re-patching same function) should work"
    mock_a2.assert_called_once()


def test_patch_everywhere_respects_stitch_hints(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that stitch_hints correctly identify stitched vs package modules."""
    # Stitched module (should skip __globals__ patching)
    stitched = ModuleType("stitched_mod")
    stitched.__file__ = "/home/user/project/dist/stitched_mod.py"

    # Package module (should do __globals__ patching)
    package_mod = ModuleType("normal_mod")
    package_mod.__file__ = "/home/user/project/src/normal_mod.py"

    def orig_func() -> str:
        return "original"

    stitched.test_func = orig_func  # type: ignore[attr-defined]
    package_mod.test_func = orig_func  # type: ignore[attr-defined]

    mock_func = MagicMock(return_value="mocked")

    # Both should work without error
    mod_apathetic_testing.patch_everywhere(
        monkeypatch,
        stitched,
        "test_func",
        mock_func,
        package_prefix="stitched_mod",
        stitch_hints={"/dist/", "stitched"},
    )

    monkeypatch.undo()

    mod_apathetic_testing.patch_everywhere(
        monkeypatch,
        package_mod,
        "test_func",
        mock_func,
        package_prefix="normal_mod",
        stitch_hints={"/dist/", "stitched"},
    )
