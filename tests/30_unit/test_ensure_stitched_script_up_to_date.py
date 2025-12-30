# tests/30_unit/test_ensure_stitched_script_up_to_date.py
"""Tests for ensure_stitched_script_up_to_date function.

Tests for ensure_stitched_script_up_to_date, including optional script_name
parameter behavior and command path usage.
"""

import json
from pathlib import Path

import pytest

import apathetic_testing.runtime as amod_utils_runtime


# --- convenience -----------------------------------------------------------

_runtime = amod_utils_runtime.ApatheticTest_Internal_Runtime


# ---------------------------------------------------------------------------
# Tests for ensure_stitched_script_up_to_date
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("script_name", "expected_script_name"),
    [
        ("custom_script", "custom_script"),
        (None, "testpkg"),  # Defaults to package_name
    ],
)
def test_ensure_stitched_script_up_to_date_script_name(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    script_name: str | None,
    expected_script_name: str,
) -> None:
    """Test ensure_stitched_script_up_to_date with and without explicit script_name."""
    # --- setup ---
    pkg_dir = tmp_path / "src" / "testpkg"
    pkg_dir.mkdir(parents=True)
    (pkg_dir / "__init__.py").write_text('"""Test package."""\n')
    (pkg_dir / "module.py").write_text('"""Test module."""\n\nvalue = 42\n')

    config = tmp_path / ".serger.jsonc"
    config_data = {
        "package": "testpkg",
        "include": ["src/testpkg/**/*.py"],
        "out": f"dist/{expected_script_name}.py",
        "disable_build_timestamp": True,
    }
    config.write_text(json.dumps(config_data, indent=2))

    monkeypatch.chdir(tmp_path)

    # --- execute ---
    if script_name is not None:
        script_path = _runtime.ensure_stitched_script_up_to_date(
            root=tmp_path,
            script_name=script_name,
            package_name="testpkg",
        )
    else:
        script_path = _runtime.ensure_stitched_script_up_to_date(
            root=tmp_path,
            package_name="testpkg",
        )

    # --- verify ---
    expected_path = tmp_path / "dist" / f"{expected_script_name}.py"
    assert script_path == expected_path
    assert script_path.exists()


def test_ensure_stitched_script_up_to_date_with_command_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test ensure_stitched_script_up_to_date with local bundler script."""
    # --- setup ---
    pkg_dir = tmp_path / "src" / "testpkg"
    pkg_dir.mkdir(parents=True)
    (pkg_dir / "__init__.py").write_text('"""Test package."""\n')
    (pkg_dir / "module.py").write_text('"""Test module."""\n\nvalue = 42\n')

    # Create a mock bundler script that reads from .serger.jsonc
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    command_path = bin_dir / "serger.py"
    command_path.write_text(
        """#!/usr/bin/env python3
import json
import sys
from pathlib import Path

# Read config from .serger.jsonc in current directory
config_path = Path(".serger.jsonc")
if not config_path.exists():
    # Try to get from --config if provided
    if "--config" in sys.argv:
        config_path = Path(sys.argv[sys.argv.index("--config") + 1])

config = json.loads(config_path.read_text())
out_path = Path(config["out"])
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text("# Mock bundled script\\n")
"""
    )
    command_path.chmod(0o755)

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
    script_path = _runtime.ensure_stitched_script_up_to_date(
        root=tmp_path,
        package_name="testpkg",
        command_path="bin/serger.py",
    )

    # --- verify ---
    expected_path = tmp_path / "dist" / "testpkg.py"
    assert script_path == expected_path
    assert script_path.exists()
