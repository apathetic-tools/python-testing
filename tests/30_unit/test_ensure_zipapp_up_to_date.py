# tests/30_unit/test_ensure_zipapp_up_to_date.py
"""Tests for ensure_zipapp_up_to_date function.

Tests for ensure_zipapp_up_to_date, including optional script_name
parameter behavior.
"""

from pathlib import Path

import pytest

import apathetic_testing.runtime as amod_utils_runtime


# --- convenience -----------------------------------------------------------

_runtime = amod_utils_runtime.ApatheticTest_Internal_Runtime


# ---------------------------------------------------------------------------
# Tests for ensure_zipapp_up_to_date
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("script_name", "expected_script_name"),
    [
        ("custom_zipapp", "custom_zipapp"),
        (None, "testpkg"),  # Defaults to package_name
    ],
)
def test_ensure_zipapp_up_to_date_script_name(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    script_name: str | None,
    expected_script_name: str,
) -> None:
    """Test ensure_zipapp_up_to_date with and without explicit script_name."""
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
    if script_name is not None:
        zipapp_path = _runtime.ensure_zipapp_up_to_date(
            root=tmp_path,
            script_name=script_name,
            package_name="testpkg",
        )
    else:
        zipapp_path = _runtime.ensure_zipapp_up_to_date(
            root=tmp_path,
            package_name="testpkg",
        )

    # --- verify ---
    expected_path = tmp_path / "dist" / f"{expected_script_name}.pyz"
    assert zipapp_path == expected_path
    assert zipapp_path.exists()
