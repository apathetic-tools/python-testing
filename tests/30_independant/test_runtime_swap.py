# tests/30_independant/test_runtime_swap.py
"""Tests for runtime_swap function.

Tests for runtime_swap, including optional script_name parameter behavior
and different runtime modes (package, stitched, zipapp).
"""

import json
from pathlib import Path

import pytest

import apathetic_testing.runtime as amod_utils_runtime
from tests.utils.constants import PROJ_ROOT


# --- convenience -----------------------------------------------------------

_runtime = amod_utils_runtime.ApatheticTest_Internal_Runtime


# ---------------------------------------------------------------------------
# Tests for runtime_swap
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("script_name", ["custom_script", None])
def test_runtime_swap_script_name(script_name: str | None) -> None:
    """Test runtime_swap with and without explicit script_name."""
    # --- execute ---
    if script_name is not None:
        result = _runtime.runtime_swap(
            root=PROJ_ROOT,
            package_name="apathetic_testing",
            script_name=script_name,
            mode="package",  # Use package mode to avoid building
        )
    else:
        result = _runtime.runtime_swap(
            root=PROJ_ROOT,
            package_name="apathetic_testing",
            mode="package",  # Use package mode to avoid building
        )

    # --- verify ---
    assert result is False  # Package mode returns False


def test_runtime_swap_stitched_without_script_name(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test runtime_swap in stitched mode defaults script_name to package_name."""
    # --- setup ---
    pkg_dir = tmp_path / "src" / "testpkg"
    pkg_dir.mkdir(parents=True)
    (pkg_dir / "__init__.py").write_text('"""Test package."""\n')
    (pkg_dir / "module.py").write_text('"""Test module."""\n\nvalue = 42\n')

    config = tmp_path / ".serger.jsonc"
    config_data = {
        "package": "testpkg",
        "include": ["src/testpkg/**/*.py"],
        "out": "dist/testpkg.py",
        "disable_build_timestamp": True,
    }
    config.write_text(json.dumps(config_data, indent=2))

    monkeypatch.chdir(tmp_path)

    # --- execute ---
    result = _runtime.runtime_swap(
        root=tmp_path,
        package_name="testpkg",
        # script_name=None (default)
        mode="stitched",
    )

    # --- verify ---
    assert result is True  # Singlefile mode returns True
    # Verify the script was created with package_name
    expected_script = tmp_path / "dist" / "testpkg.py"
    assert expected_script.exists()


def test_runtime_swap_zipapp_without_script_name(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test runtime_swap in zipapp mode defaults script_name to package_name.

    Note: This test verifies the path logic works correctly. Full zipapp
    import testing is covered in integration tests.
    """
    # --- setup ---
    pkg_dir = tmp_path / "src" / "testpkg"
    pkg_dir.mkdir(parents=True)
    (pkg_dir / "__init__.py").write_text('"""Test package."""\n')
    (pkg_dir / "module.py").write_text('"""Test module."""\n\nvalue = 42\n')

    # Create a minimal pyproject.toml for zipbundler with entry point
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """[project]
name = "testpkg"
version = "0.1.0"

[project.scripts]
testpkg = "testpkg:main"
"""
    )
    # Add a main function
    (pkg_dir / "__main__.py").write_text("def main(): pass\n")
    # Ensure dist directory exists
    (tmp_path / "dist").mkdir(exist_ok=True)

    monkeypatch.chdir(tmp_path)

    # --- execute ---
    result = _runtime.runtime_swap(
        root=tmp_path,
        package_name="testpkg",
        # script_name=None (default)
        mode="zipapp",
    )

    # --- verify ---
    assert result is True  # Zipapp mode returns True
    # Verify the zipapp was created with package_name
    expected_zipapp = tmp_path / "dist" / "testpkg.pyz"
    assert expected_zipapp.exists(), "Zipapp should be created with package_name"
