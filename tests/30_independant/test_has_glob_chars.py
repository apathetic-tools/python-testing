# tests/30_independant/test_has_glob_chars.py
"""Tests for has_glob_chars utility function."""

import pytest

import apathetic_testing as mod_autils


@pytest.mark.parametrize(
    ("pattern", "expected"),
    [
        # Patterns with glob characters - should return True
        ("*.py", True),
        ("file*.txt", True),
        ("**/*.py", True),
        ("file?.txt", True),
        ("test_?.py", True),
        ("file[0-9].txt", True),
        ("test_[abc].py", True),
        # Patterns without glob characters - should return False
        ("file.txt", False),
        ("path/to/file", False),
        ("", False),
        ("normal_string", False),
        ("plain_text_no_glob", False),
        ("path/to/file.txt", False),
        ("normal_directory_name", False),
        ("123456", False),
    ],
)
def test_has_glob_chars(pattern: str, expected: bool) -> None:  # noqa: FBT001
    """has_glob_chars() should correctly detect glob characters in patterns."""
    # --- execute and verify ---
    assert mod_autils.has_glob_chars(pattern) == expected


def test_has_glob_chars_false_return_path() -> None:
    """has_glob_chars() should return False when no glob chars found."""
    # --- execute and verify ---
    result = mod_autils.has_glob_chars("plain_text_no_glob")
    assert result is False
    # Test with various strings that don't contain glob chars
    assert not mod_autils.has_glob_chars("path/to/file.txt")
    assert not mod_autils.has_glob_chars("normal_directory_name")
    assert not mod_autils.has_glob_chars("123456")
    assert not mod_autils.has_glob_chars("")
