# tests/30_independant/test_schema_from_typeddict.py
"""Tests for schema_from_typeddict utility function."""

from typing import TypedDict

import apathetic_testing as mod_autils


def test_schema_from_typeddict_basic() -> None:
    """schema_from_typeddict() should extract field types from TypedDict."""

    class Config(TypedDict):
        name: str
        value: int
        enabled: bool

    # --- execute ---
    result = mod_autils.schema_from_typeddict(Config)

    # --- verify ---
    assert isinstance(result, dict)
    assert "name" in result
    assert "value" in result
    assert "enabled" in result
    assert result["name"] is str
    assert result["value"] is int
    assert result["enabled"] is bool


def test_schema_from_typeddict_with_optional() -> None:
    """schema_from_typeddict() should handle Optional fields."""

    class Config(TypedDict):
        required: str
        optional: str | None

    # --- execute ---
    result = mod_autils.schema_from_typeddict(Config)

    # --- verify ---
    assert "required" in result
    assert "optional" in result
    # Optional[str] is represented as str | None or Union[str, None]
    assert result["required"] is str


def test_schema_from_typeddict_empty() -> None:
    """schema_from_typeddict() should handle empty TypedDict."""

    class Empty(TypedDict):
        pass

    # --- execute ---
    result = mod_autils.schema_from_typeddict(Empty)

    # --- verify ---
    assert isinstance(result, dict)
    assert len(result) == 0


def test_schema_from_typeddict_return_type() -> None:
    """schema_from_typeddict() should return dict with type hints."""
    # This test ensures line 53 (return statement) is covered

    class Config(TypedDict):
        field1: str
        field2: int

    # --- execute ---
    result = mod_autils.schema_from_typeddict(Config)

    # --- verify ---
    # Ensure the return statement is executed
    assert isinstance(result, dict)
    assert result == {"field1": str, "field2": int}
