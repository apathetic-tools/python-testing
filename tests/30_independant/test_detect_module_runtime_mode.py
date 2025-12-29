"""Tests for detect_module_runtime_mode function."""

from __future__ import annotations

from types import ModuleType

import pytest

import apathetic_testing as mod_apathetic_testing


@pytest.mark.parametrize(
    ("module_attrs", "expected_mode"),
    [
        # Regular module
        ({"__file__": "/path/to/regular_module.py"}, "package"),
        # Stitched module
        ({"__STITCHED__": True}, "stitched"),
        # Standalone module
        ({"__STANDALONE__": True}, "stitched"),
        # Zipapp module (with .pyz in path)
        ({"__file__": "/path/to/archive.pyz/module.py"}, "zipapp"),
        # Zipapp module (ending with .pyz)
        ({"__file__": "/path/to/archive.pyz"}, "zipapp"),
    ],
)
def test_detect_module_runtime_mode(
    module_attrs: dict[str, object], expected_mode: str
) -> None:
    """Return correct mode for different module types."""
    # --- setup ---
    module = ModuleType("test_module")
    for attr, value in module_attrs.items():
        setattr(module, attr, value)

    # --- execute ---
    result = mod_apathetic_testing.detect_module_runtime_mode(module)

    # --- verify ---
    assert result == expected_mode


def test_detect_module_runtime_mode_prefers_marker_over_path() -> None:
    """detect_module_runtime_mode should prefer markers over path heuristics."""
    # Module with .pyz in path but __STITCHED__ marker
    conflicting_module = ModuleType("conflicting_module")
    conflicting_module.__file__ = "/path/to/archive.pyz/module.py"
    conflicting_module.__STITCHED__ = True  # type: ignore[attr-defined]

    result = mod_apathetic_testing.detect_module_runtime_mode(conflicting_module)
    assert result == "stitched", "Markers should take precedence over path heuristics"


def test_detect_module_runtime_mode_raises_on_non_module() -> None:
    """detect_module_runtime_mode should raise TypeError for non-modules."""
    with pytest.raises(TypeError, match="Expected ModuleType"):
        mod_apathetic_testing.detect_module_runtime_mode("not a module")  # type: ignore[arg-type]
