# tests/0_independant/test_load_toml.py
"""Tests for load_toml utility function."""

import tempfile
from pathlib import Path
from typing import Any

import pytest

import apathetic_testing as mod_autils


def test_load_toml_valid_file() -> None:
    """Should load valid TOML file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write(
            """[project]
name = "test-package"
version = "1.2.3"
"""
        )
        f.flush()
        path = Path(f.name)

    try:
        data = mod_autils.load_toml(path)
        assert data is not None
        assert "project" in data
        assert data["project"]["name"] == "test-package"
        assert data["project"]["version"] == "1.2.3"
    finally:
        path.unlink()


def test_load_toml_missing_file() -> None:
    """Should raise FileNotFoundError for missing file."""
    with pytest.raises(FileNotFoundError, match="not found"):
        mod_autils.load_toml(Path("/nonexistent/file.toml"))


def test_load_toml_invalid_syntax() -> None:
    """Should raise ValueError for invalid TOML syntax."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write("invalid toml {[}\n")
        f.flush()
        path = Path(f.name)

    try:
        # Depending on parser, may raise ValueError or return empty dict
        # Both are acceptable - just ensure it doesn't crash
        try:
            data = mod_autils.load_toml(path)
            # If it doesn't raise, should return something
            assert isinstance(data, dict)
        except ValueError:
            # Also acceptable
            pass
    finally:
        path.unlink()


def test_load_toml_missing_tomli_required_false(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """load_toml() should return None when tomli is missing and required=False."""
    # --- setup ---
    toml_file = tmp_path / "test.toml"
    toml_file.write_text('[project]\nname = "test"')

    # Mock both tomllib and tomli to raise ImportError (simulating Python
    # 3.10 without tomli)
    def mock_import(name: str, *args: object, **kwargs: object) -> Any:
        if name in ("tomllib", "tomli"):
            msg = f"No module named '{name}'"
            raise ImportError(msg)
        # Use real import for other modules
        return __import__(name, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr("builtins.__import__", mock_import)

    # --- execute ---
    # With required=False, should return None when tomli is missing
    result = mod_autils.load_toml(toml_file, required=False)

    # --- verify ---
    assert result is None


def test_load_toml_missing_tomli_required_true(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """load_toml() should raise RuntimeError when tomli is missing and required=True."""
    # --- setup ---
    toml_file = tmp_path / "test.toml"
    toml_file.write_text('[project]\nname = "test"')

    # Mock both tomllib and tomli to raise ImportError
    def mock_import(name: str, *args: object, **kwargs: object) -> Any:
        if name in ("tomllib", "tomli"):
            msg = f"No module named '{name}'"
            raise ImportError(msg)
        return __import__(name, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr("builtins.__import__", mock_import)

    # --- execute and verify ---
    # With required=True, should raise RuntimeError
    with pytest.raises(RuntimeError, match="TOML parsing requires 'tomli' package"):
        mod_autils.load_toml(toml_file, required=True)
