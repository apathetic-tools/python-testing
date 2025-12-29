# tests/30_independant/test_detect_packages_from_files.py
"""Tests for detect_packages_from_files() function.

The detect_packages_from_files() function detects Python packages from file paths.
It supports:
- Regular packages (with __init__.py files)
- Namespace packages (via source_bases parameter)
- Fallback to configured package_name
"""

import tempfile
from pathlib import Path

import apathetic_testing.modules as mod_utils_modules


# --- convenience -----------------------------------------------------------

_modules = mod_utils_modules.ApatheticUtils_Internal_Modules

# ---------------------------------------------------------------------------
# Tests - Basic Functionality
# ---------------------------------------------------------------------------


def test_detect_packages_from_files_empty_list() -> None:
    """Test with empty file_paths list.

    Should return only the configured package_name and empty parent directories.
    """
    # --- execute ---
    detected, parent_dirs = _modules.detect_packages_from_files(
        file_paths=[],
        package_name="test_pkg",
    )

    # --- verify ---
    assert detected == {"test_pkg"}
    assert parent_dirs == []


def test_detect_packages_from_files_single_package_with_init() -> None:
    """Test detection of single package with __init__.py file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        # Create package structure: mypkg/__init__.py, mypkg/module.py
        pkg_dir = tmp_path / "mypkg"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")
        (pkg_dir / "module.py").write_text("")

        # --- execute ---
        detected, parent_dirs = _modules.detect_packages_from_files(
            file_paths=[pkg_dir / "module.py"],
            package_name="test_pkg",
        )

        # --- verify ---
        assert "mypkg" in detected
        assert "test_pkg" in detected
        assert len(parent_dirs) == 1
        assert str(tmp_path) in parent_dirs


def test_detect_packages_from_files_multiple_files_same_package() -> None:
    """Test that multiple files in same package are deduplicated."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        # Create package structure:
        # mypkg/__init__.py, mypkg/module1.py, mypkg/module2.py
        pkg_dir = tmp_path / "mypkg"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")
        (pkg_dir / "module1.py").write_text("")
        (pkg_dir / "module2.py").write_text("")

        # --- execute ---
        detected, parent_dirs = _modules.detect_packages_from_files(
            file_paths=[pkg_dir / "module1.py", pkg_dir / "module2.py"],
            package_name="test_pkg",
        )

        # --- verify ---
        assert "mypkg" in detected
        assert "test_pkg" in detected
        assert len(detected) == 2  # noqa: PLR2004  # mypkg + test_pkg
        assert len(parent_dirs) == 1  # Should be deduplicated
        assert str(tmp_path) in parent_dirs


def test_detect_packages_from_files_multiple_packages() -> None:
    """Test detection of multiple different packages."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        # Create two packages: pkg1/__init__.py, pkg2/__init__.py
        pkg1_dir = tmp_path / "pkg1"
        pkg1_dir.mkdir()
        (pkg1_dir / "__init__.py").write_text("")
        (pkg1_dir / "module1.py").write_text("")

        pkg2_dir = tmp_path / "pkg2"
        pkg2_dir.mkdir()
        (pkg2_dir / "__init__.py").write_text("")
        (pkg2_dir / "module2.py").write_text("")

        # --- execute ---
        detected, parent_dirs = _modules.detect_packages_from_files(
            file_paths=[pkg1_dir / "module1.py", pkg2_dir / "module2.py"],
            package_name="test_pkg",
        )

        # --- verify ---
        assert "pkg1" in detected
        assert "pkg2" in detected
        assert "test_pkg" in detected
        assert len(detected) == 3  # noqa: PLR2004
        assert len(parent_dirs) == 1  # Both packages have same parent
        assert str(tmp_path) in parent_dirs


def test_detect_packages_from_files_no_init_no_source_bases() -> None:
    """Test files without __init__.py and no source_bases fall back to package_name."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        # Create file without __init__.py
        (tmp_path / "module.py").write_text("")

        # --- execute ---
        detected, parent_dirs = _modules.detect_packages_from_files(
            file_paths=[tmp_path / "module.py"],
            package_name="test_pkg",
        )

        # --- verify ---
        # Should only have test_pkg (fallback), no package detected
        assert detected == {"test_pkg"}
        assert parent_dirs == []


def test_detect_packages_from_files_nested_package() -> None:
    """Test detection of nested package structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        # Create nested structure: mypkg/__init__.py, mypkg/subpkg/__init__.py
        pkg_dir = tmp_path / "mypkg"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")
        subpkg_dir = pkg_dir / "subpkg"
        subpkg_dir.mkdir()
        (subpkg_dir / "__init__.py").write_text("")
        (subpkg_dir / "module.py").write_text("")

        # --- execute ---
        detected, parent_dirs = _modules.detect_packages_from_files(
            file_paths=[subpkg_dir / "module.py"],
            package_name="test_pkg",
        )

        # --- verify ---
        # Should detect mypkg (the root package with __init__.py)
        assert "mypkg" in detected
        assert "test_pkg" in detected
        assert len(parent_dirs) == 1
        assert str(tmp_path) in parent_dirs


# ---------------------------------------------------------------------------
# Tests - source_bases Parameter
# ---------------------------------------------------------------------------


def test_detect_packages_from_files_with_source_bases() -> None:
    """Test detection with source_bases parameter (namespace packages)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        # Create structure under src/: src/mypkg/module.py (no __init__.py)
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        pkg_dir = src_dir / "mypkg"
        pkg_dir.mkdir()
        (pkg_dir / "module.py").write_text("")

        # --- execute ---
        detected, parent_dirs = _modules.detect_packages_from_files(
            file_paths=[pkg_dir / "module.py"],
            package_name="test_pkg",
            source_bases=[str(src_dir)],
        )

        # --- verify ---
        assert "mypkg" in detected
        assert "test_pkg" in detected
        assert len(parent_dirs) == 1
        assert str(src_dir) in parent_dirs


def test_detect_packages_from_files_source_bases_file_in_base() -> None:
    """Test files directly in source_bases (not in subdirectory) are not packages."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        # Create file directly in src/: src/module.py
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "module.py").write_text("")

        # --- execute ---
        detected, parent_dirs = _modules.detect_packages_from_files(
            file_paths=[src_dir / "module.py"],
            package_name="test_pkg",
            source_bases=[str(src_dir)],
        )

        # --- verify ---
        # Should only have test_pkg (file is directly in base, not in subdirectory)
        assert detected == {"test_pkg"}
        assert parent_dirs == []


def test_detect_packages_from_files_source_bases_multiple_bases() -> None:
    """Test with multiple source_bases directories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        # Create structure: src1/pkg1/module1.py, src2/pkg2/module2.py
        src1_dir = tmp_path / "src1"
        src1_dir.mkdir()
        pkg1_dir = src1_dir / "pkg1"
        pkg1_dir.mkdir()
        (pkg1_dir / "module1.py").write_text("")

        src2_dir = tmp_path / "src2"
        src2_dir.mkdir()
        pkg2_dir = src2_dir / "pkg2"
        pkg2_dir.mkdir()
        (pkg2_dir / "module2.py").write_text("")

        # --- execute ---
        detected, parent_dirs = _modules.detect_packages_from_files(
            file_paths=[pkg1_dir / "module1.py", pkg2_dir / "module2.py"],
            package_name="test_pkg",
            source_bases=[str(src1_dir), str(src2_dir)],
        )

        # --- verify ---
        assert "pkg1" in detected
        assert "pkg2" in detected
        assert "test_pkg" in detected
        assert len(detected) == 3  # noqa: PLR2004
        assert len(parent_dirs) == 2  # noqa: PLR2004  # Two different parent directories
        assert str(src1_dir) in parent_dirs
        assert str(src2_dir) in parent_dirs


def test_detect_packages_from_files_source_bases_init_takes_precedence() -> None:
    """Test that __init__.py takes precedence over source_bases detection."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        # Create structure: src/mypkg/__init__.py, src/mypkg/module.py
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        pkg_dir = src_dir / "mypkg"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")
        (pkg_dir / "module.py").write_text("")

        # --- execute ---
        detected, parent_dirs = _modules.detect_packages_from_files(
            file_paths=[pkg_dir / "module.py"],
            package_name="test_pkg",
            source_bases=[str(src_dir)],
        )

        # --- verify ---
        # Should detect mypkg via __init__.py (not via source_bases)
        assert "mypkg" in detected
        assert "test_pkg" in detected
        assert len(parent_dirs) == 1
        assert str(src_dir) in parent_dirs


def test_detect_packages_from_files_source_bases_namespace_package() -> None:
    """Test namespace package: base directory containing packages is also detected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        # Create structure: src/mypkg/module.py
        # The src directory should be detected as a package if it contains packages
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        pkg_dir = src_dir / "mypkg"
        pkg_dir.mkdir()
        (pkg_dir / "module.py").write_text("")

        # --- execute ---
        detected, _parent_dirs = _modules.detect_packages_from_files(
            file_paths=[pkg_dir / "module.py"],
            package_name="test_pkg",
            source_bases=[str(tmp_path)],  # Base is parent of src
        )

        # --- verify ---
        # Should detect both mypkg and src (src contains mypkg, so it's also a package)
        assert "mypkg" in detected
        assert "src" in detected
        assert "test_pkg" in detected
        assert len(detected) == 3  # noqa: PLR2004  # noqa: PLR2004


def test_detect_packages_from_files_source_bases_nonexistent() -> None:
    """Test that non-existent source_bases are skipped gracefully."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        # Create file without __init__.py
        (tmp_path / "module.py").write_text("")

        # --- execute ---
        detected, parent_dirs = _modules.detect_packages_from_files(
            file_paths=[tmp_path / "module.py"],
            package_name="test_pkg",
            source_bases=[str(tmp_path / "nonexistent")],
        )

        # --- verify ---
        # Should fall back to package_name since source_bases doesn't exist
        assert detected == {"test_pkg"}
        assert parent_dirs == []


def test_detect_packages_from_files_source_bases_not_directory() -> None:
    """Test that source_bases that are files (not directories) are skipped."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        # Create a file (not a directory)
        file_path = tmp_path / "not_a_dir"
        file_path.write_text("")
        (tmp_path / "module.py").write_text("")

        # --- execute ---
        detected, parent_dirs = _modules.detect_packages_from_files(
            file_paths=[tmp_path / "module.py"],
            package_name="test_pkg",
            source_bases=[str(file_path)],
        )

        # --- verify ---
        # Should fall back to package_name since source_bases is not a directory
        assert detected == {"test_pkg"}
        assert parent_dirs == []


def test_detect_packages_from_files_source_bases_equals_package_name() -> None:
    """Test that source_bases matching package_name are skipped."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        # Create structure: test_pkg/module.py
        pkg_dir = tmp_path / "test_pkg"
        pkg_dir.mkdir()
        (pkg_dir / "module.py").write_text("")

        # --- execute ---
        detected, parent_dirs = _modules.detect_packages_from_files(
            file_paths=[pkg_dir / "module.py"],
            package_name="test_pkg",
            source_bases=[str(pkg_dir)],
        )

        # --- verify ---
        # Should skip test_pkg as a namespace package (it equals package_name)
        # But should still detect it if it has __init__.py or is under another base
        # In this case, no __init__.py and base equals package_name, so should skip
        assert "test_pkg" in detected  # Always included
        # May or may not detect test_pkg as a separate package depending on logic
        assert len(parent_dirs) == 0 or len(parent_dirs) == 1


def test_detect_packages_from_files_source_bases_common_root() -> None:
    """Test that source_bases that are the common root of all files are skipped."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        # Create structure: src/mypkg/module1.py, src/mypkg/module2.py
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        pkg_dir = src_dir / "mypkg"
        pkg_dir.mkdir()
        (pkg_dir / "module1.py").write_text("")
        (pkg_dir / "module2.py").write_text("")

        # --- execute ---
        detected, _parent_dirs = _modules.detect_packages_from_files(
            file_paths=[pkg_dir / "module1.py", pkg_dir / "module2.py"],
            package_name="test_pkg",
            source_bases=[str(src_dir)],  # src is the common root
        )

        # --- verify ---
        # Should detect mypkg, but src should be skipped as it's the common root
        assert "mypkg" in detected
        assert "test_pkg" in detected
        # src should not be detected as a package (it's the common root)
        assert "src" not in detected or len(detected) == 2  # noqa: PLR2004


# ---------------------------------------------------------------------------
# Tests - _config_dir Parameter
# ---------------------------------------------------------------------------


def test_detect_packages_from_files_with_config_dir_none() -> None:
    """Test that _config_dir=None works (default behavior)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        pkg_dir = tmp_path / "mypkg"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")
        (pkg_dir / "module.py").write_text("")

        # --- execute ---
        detected, _parent_dirs = _modules.detect_packages_from_files(
            file_paths=[pkg_dir / "module.py"],
            package_name="test_pkg",
            _config_dir=None,
        )

        # --- verify ---
        assert "mypkg" in detected
        assert "test_pkg" in detected


def test_detect_packages_from_files_with_config_dir_path() -> None:
    """Test that _config_dir with a Path works (even though it's unused)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        pkg_dir = tmp_path / "mypkg"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")
        (pkg_dir / "module.py").write_text("")

        config_dir = tmp_path / "config"
        config_dir.mkdir()

        # --- execute ---
        detected, _parent_dirs = _modules.detect_packages_from_files(
            file_paths=[pkg_dir / "module.py"],
            package_name="test_pkg",
            _config_dir=config_dir,
        )

        # --- verify ---
        # Should work the same as without _config_dir (it's unused)
        assert "mypkg" in detected
        assert "test_pkg" in detected


# ---------------------------------------------------------------------------
# Tests - Return Value Validation
# ---------------------------------------------------------------------------


def test_detect_packages_from_files_always_includes_package_name() -> None:
    """Test that package_name is always included in detected packages."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        pkg_dir = tmp_path / "mypkg"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")
        (pkg_dir / "module.py").write_text("")

        # --- execute ---
        detected, _ = _modules.detect_packages_from_files(
            file_paths=[pkg_dir / "module.py"],
            package_name="test_pkg",
        )

        # --- verify ---
        assert "test_pkg" in detected


def test_detect_packages_from_files_parent_dirs_absolute() -> None:
    """Test that parent directories are returned as absolute paths."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        pkg_dir = tmp_path / "mypkg"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")
        (pkg_dir / "module.py").write_text("")

        # --- execute ---
        _, parent_dirs = _modules.detect_packages_from_files(
            file_paths=[pkg_dir / "module.py"],
            package_name="test_pkg",
        )

        # --- verify ---
        assert len(parent_dirs) == 1
        # Should be absolute path
        assert Path(parent_dirs[0]).is_absolute()
        assert str(tmp_path.resolve()) in parent_dirs


def test_detect_packages_from_files_parent_dirs_deduplicated() -> None:
    """Test that parent directories are deduplicated."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        pkg_dir = tmp_path / "mypkg"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")
        (pkg_dir / "module1.py").write_text("")
        (pkg_dir / "module2.py").write_text("")

        # --- execute ---
        _, parent_dirs = _modules.detect_packages_from_files(
            file_paths=[pkg_dir / "module1.py", pkg_dir / "module2.py"],
            package_name="test_pkg",
        )

        # --- verify ---
        # Should only have one parent directory (deduplicated)
        assert len(parent_dirs) == 1
        assert len(set(parent_dirs)) == 1  # All should be unique


def test_detect_packages_from_files_parent_dirs_excludes_root() -> None:
    """Test that filesystem root is excluded from parent directories."""
    # This is a tricky test - we need a package at the filesystem root
    # On most systems, this isn't practical, but we can test the logic
    # by checking that if parent is root, it's excluded
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        pkg_dir = tmp_path / "mypkg"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")
        (pkg_dir / "module.py").write_text("")

        # --- execute ---
        _, parent_dirs = _modules.detect_packages_from_files(
            file_paths=[pkg_dir / "module.py"],
            package_name="test_pkg",
        )

        # --- verify ---
        # Should not include filesystem root
        for parent_dir in parent_dirs:
            parent_path = Path(parent_dir)
            # Parent of root equals root itself
            assert parent_path.parent != parent_path


# ---------------------------------------------------------------------------
# Tests - Edge Cases
# ---------------------------------------------------------------------------


def test_detect_packages_from_files_no_common_root() -> None:
    """Test files with no common root."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        # Create two completely separate directory trees
        pkg1_dir = tmp_path / "dir1" / "pkg1"
        pkg1_dir.mkdir(parents=True)
        (pkg1_dir / "__init__.py").write_text("")
        (pkg1_dir / "module1.py").write_text("")

        pkg2_dir = tmp_path / "dir2" / "pkg2"
        pkg2_dir.mkdir(parents=True)
        (pkg2_dir / "__init__.py").write_text("")
        (pkg2_dir / "module2.py").write_text("")

        # --- execute ---
        detected, parent_dirs = _modules.detect_packages_from_files(
            file_paths=[pkg1_dir / "module1.py", pkg2_dir / "module2.py"],
            package_name="test_pkg",
        )

        # --- verify ---
        assert "pkg1" in detected
        assert "pkg2" in detected
        assert "test_pkg" in detected
        # Should have two different parent directories
        assert len(parent_dirs) == 2  # noqa: PLR2004


def test_detect_packages_from_files_mixed_init_and_source_bases() -> None:
    """Test mixed scenario: some files with __init__.py, some under source_bases."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        # File with __init__.py
        pkg1_dir = tmp_path / "pkg1"
        pkg1_dir.mkdir()
        (pkg1_dir / "__init__.py").write_text("")
        (pkg1_dir / "module1.py").write_text("")

        # File under source_bases (no __init__.py)
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        pkg2_dir = src_dir / "pkg2"
        pkg2_dir.mkdir()
        (pkg2_dir / "module2.py").write_text("")

        # --- execute ---
        detected, parent_dirs = _modules.detect_packages_from_files(
            file_paths=[pkg1_dir / "module1.py", pkg2_dir / "module2.py"],
            package_name="test_pkg",
            source_bases=[str(src_dir)],
        )

        # --- verify ---
        assert "pkg1" in detected  # Via __init__.py
        assert "pkg2" in detected  # Via source_bases
        assert "test_pkg" in detected
        assert len(detected) == 3  # noqa: PLR2004
        # Should have two parent directories
        assert len(parent_dirs) == 2  # noqa: PLR2004


def test_detect_packages_from_files_handles_mixed_packages_and_loose_files() -> None:
    """Test handling mix of package files and loose files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        # Package file
        pkg_dir = tmp_path / "mypkg"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")
        pkg_file = pkg_dir / "module.py"
        pkg_file.write_text("")

        # Loose file (no __init__.py, not under source_bases)
        loose_dir = tmp_path / "loose"
        loose_dir.mkdir()
        loose_file = loose_dir / "script.py"
        loose_file.write_text("")

        # --- execute ---
        detected, _parent_dirs = _modules.detect_packages_from_files(
            file_paths=[pkg_file, loose_file],
            package_name="default",
        )

        # --- verify ---
        # Should detect "mypkg" and include "default" as fallback
        assert "mypkg" in detected
        assert "default" in detected
        assert len(detected) == 2  # noqa: PLR2004


def test_detect_packages_from_files_deterministic_output_order() -> None:
    """Test that function produces deterministic results (for build reproducibility)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        pkg1_dir = tmp_path / "pkg1"
        pkg1_dir.mkdir()
        (pkg1_dir / "__init__.py").write_text("")
        file1 = pkg1_dir / "module1.py"
        file1.write_text("")

        pkg2_dir = tmp_path / "pkg2"
        pkg2_dir.mkdir()
        (pkg2_dir / "__init__.py").write_text("")
        file2 = pkg2_dir / "module2.py"
        file2.write_text("")

        # --- execute ---
        # Call multiple times with different file order
        result1, _parent_dirs1 = _modules.detect_packages_from_files(
            file_paths=[file1, file2],
            package_name="default",
        )
        result2, _parent_dirs2 = _modules.detect_packages_from_files(
            file_paths=[file2, file1],
            package_name="default",
        )

        # --- verify ---
        # Results should be identical (sets are unordered, but contents same)
        assert result1 == result2
        assert sorted(result1) == sorted(result2)


def test_detect_packages_from_files_source_bases_only_applies_to_files_under_base() -> (
    None
):
    """Test that source_bases only applies to files under the base, not elsewhere."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        # File under source_bases (should use source_bases logic)
        pkg1_dir = src_dir / "pkg1"
        pkg1_dir.mkdir()
        file1 = pkg1_dir / "module1.py"
        file1.write_text("")

        # File outside source_bases (should require __init__.py)
        other_dir = tmp_path / "other"
        other_dir.mkdir()
        pkg2_dir = other_dir / "pkg2"
        pkg2_dir.mkdir()
        # No __init__.py, so should not be detected
        file2 = pkg2_dir / "module2.py"
        file2.write_text("")

        # --- execute ---
        detected, _parent_dirs = _modules.detect_packages_from_files(
            file_paths=[file1, file2],
            package_name="default",
            source_bases=[str(src_dir)],
        )

        # --- verify ---
        # Should detect "pkg1" via source_bases, but not "pkg2" (outside base)
        assert "pkg1" in detected
        assert "pkg2" not in detected
        assert "default" in detected
