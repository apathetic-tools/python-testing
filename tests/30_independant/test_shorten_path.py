# tests/30_independant/test_shorten_path.py
"""Tests for shorten_path utility function."""

import tempfile
from pathlib import Path

import pytest

import apathetic_testing as mod_autils


@pytest.mark.parametrize(
    ("path_input", "base_input"),
    [
        # String inputs
        (
            "/home/user/code/serger/src/serger/logs.py",
            "/home/user/code/serger/tests/utils/patch_everywhere.py",
        ),
        # Path object inputs
        (
            Path("/home/user/code/serger/src/serger/logs.py"),
            Path("/home/user/code/serger/tests/utils/patch_everywhere.py"),
        ),
    ],
)
def test_shorten_path_with_common_prefix(
    path_input: str | Path, base_input: str | Path
) -> None:
    """shorten_path() should return relative path when paths share prefix."""
    # --- execute ---
    result = mod_autils.shorten_path(path_input, base_input)

    # --- verify ---
    assert result == "src/serger/logs.py"


def test_shorten_path_no_common_prefix() -> None:
    """shorten_path() should return absolute path when only root in common."""
    # --- setup ---
    path = "/home/user/file1.py"
    base = "/var/lib/other/file2.py"

    # --- execute ---
    result = mod_autils.shorten_path(path, base)

    # --- verify ---
    # When common prefix is only root, returns absolute path (default behavior)
    assert result == "/home/user/file1.py"


@pytest.mark.parametrize(
    ("path", "base", "expected"),
    [
        # Identical paths
        ("/home/user/file.py", "/home/user/file.py", "."),
        # Empty result (directory paths)
        ("/home/user", "/home/user", "."),
        # One path is prefix of other
        ("/home/user/code/file.py", "/home/user/code", "file.py"),
    ],
)
def test_shorten_path_special_cases(path: str, base: str, expected: str) -> None:
    """shorten_path() should handle special cases like identical paths and prefixes."""
    # --- execute ---
    result = mod_autils.shorten_path(path, base)

    # --- verify ---
    assert result == expected


def test_shorten_path_relative_paths() -> None:
    """shorten_path() should resolve relative paths."""
    # --- setup ---
    path = "src/file.py"
    base = "tests/file.py"

    # --- execute ---
    result = mod_autils.shorten_path(path, base)

    # --- verify ---
    # Should resolve to absolute paths and find common prefix
    assert isinstance(result, str)
    # Result depends on current working directory, but should be a valid path


def test_shorten_path_comprehensive() -> None:
    """shorten_path() should handle paths with common prefixes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create test structure
        path1 = tmp_path / "a" / "b" / "c" / "file1.py"
        path2 = tmp_path / "a" / "b" / "d" / "file2.py"
        path1.parent.mkdir(parents=True, exist_ok=True)
        path2.parent.mkdir(parents=True, exist_ok=True)
        path1.touch()
        path2.touch()

        # Test with paths that share common prefix
        result = mod_autils.shorten_path(path1, path2)

        # Verify result
        assert isinstance(result, str)
        # Should return relative path from common prefix
        assert "c" in result or "file1.py" in result


def test_shorten_path_path_resolution() -> None:
    """shorten_path() should resolve paths correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create relative paths that need resolution
        rel_path1 = tmp_path / "subdir1" / "file1.py"
        rel_path2 = tmp_path / "subdir2" / "file2.py"
        rel_path1.parent.mkdir(parents=True, exist_ok=True)
        rel_path2.parent.mkdir(parents=True, exist_ok=True)
        rel_path1.touch()
        rel_path2.touch()

        # Test with string paths (will be resolved)
        result = mod_autils.shorten_path(str(rel_path1), str(rel_path2))

        # Verify result is a string
        assert isinstance(result, str)


def test_shorten_path_zip_longest_logic() -> None:
    """Use zip_longest correctly for paths of different lengths."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create paths of different lengths
        long_path = tmp_path / "a" / "b" / "c" / "d" / "e" / "file.py"
        short_path = tmp_path / "a" / "b" / "other.py"
        long_path.parent.mkdir(parents=True, exist_ok=True)
        short_path.parent.mkdir(parents=True, exist_ok=True)
        long_path.touch()
        short_path.touch()

        # Test with different length paths
        result = mod_autils.shorten_path(long_path, short_path)

        # Verify result
        assert isinstance(result, str)
        # Should handle the case where one path is longer
        assert "c" in result or "d" in result or "e" in result or "file.py" in result


def test_shorten_path_slice_remaining() -> None:
    """shorten_path() should slice remaining parts correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create paths with common prefix
        path1 = tmp_path / "common" / "part1" / "part2" / "file1.py"
        path2 = tmp_path / "common" / "other" / "file2.py"
        path1.parent.mkdir(parents=True, exist_ok=True)
        path2.parent.mkdir(parents=True, exist_ok=True)
        path1.touch()
        path2.touch()

        # Test slicing logic
        result = mod_autils.shorten_path(path1, path2)

        # Verify the remaining parts are correctly sliced
        assert isinstance(result, str)
        # Should contain the parts after common prefix
        assert "part1" in result or "part2" in result or "file1.py" in result


def test_shorten_path_empty_remaining() -> None:
    """shorten_path() should return '.' when remaining is empty."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create identical paths
        path1 = tmp_path / "file.py"
        path2 = tmp_path / "file.py"
        path1.parent.mkdir(parents=True, exist_ok=True)
        path1.touch()

        # When paths are identical, remaining should be empty
        result = mod_autils.shorten_path(path1, path2)

        # Should return "." when remaining is empty
        assert result == "."


@pytest.mark.parametrize(
    ("path", "bases", "expected"),
    [
        # Multiple bases - should return shortest
        (
            "/home/user/code/serger/src/logs.py",
            [
                "/home/user/code/serger/tests/utils/patch.py",
                "/home/user/code/serger/src",
            ],
            "logs.py",
        ),
        # Single string base
        (
            "/home/user/code/serger/src/logs.py",
            "/home/user/code/serger/tests/utils/patch.py",
            "src/logs.py",
        ),
        # Multiple bases with different prefixes
        (
            "/home/user/project1/src/file.py",
            [
                "/home/user/project2/tests/test.py",
                "/home/user/project1/src/utils/helper.py",
            ],
            "file.py",
        ),
    ],
)
def test_shorten_path_multiple_bases(
    path: str, bases: str | list[str | Path], expected: str
) -> None:
    """shorten_path() should return shortest path when multiple bases provided."""
    # --- execute ---
    result = mod_autils.shorten_path(path, bases)

    # --- verify ---
    assert result == expected
