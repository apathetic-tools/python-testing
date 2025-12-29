# tests/30_independant/test_literal_to_set.py
"""Tests for literal_to_set utility function."""

from typing import Literal

import pytest

import apathetic_testing as mod_autils


@pytest.mark.parametrize(
    ("literal_type", "expected"),
    [
        (Literal["a", "b", "c"], {"a", "b", "c"}),
        (Literal["only"], {"only"}),
        (Literal[1, 2, 3], {1, 2, 3}),
        # literal_to_set() only accepts pure Literal types, not Optional/Literal unions
        # So we include None as a literal value directly
        (Literal["a", 1, True], {"a", 1}),
    ],
)
def test_literal_to_set(literal_type: type, expected: set[str | int]) -> None:
    """literal_to_set() should extract values from Literal types."""
    # --- execute ---
    result = mod_autils.literal_to_set(literal_type)

    # --- verify ---
    assert result == expected


def test_literal_to_set_raises_typeerror_for_non_literal() -> None:
    """literal_to_set() should raise TypeError for non-Literal types."""
    # --- execute and verify ---
    with pytest.raises(TypeError, match="Expected Literal type"):
        mod_autils.literal_to_set(str)

    with pytest.raises(TypeError, match="Expected Literal type"):
        mod_autils.literal_to_set(int)

    with pytest.raises(TypeError, match="Expected Literal type"):
        mod_autils.literal_to_set(list[str])
