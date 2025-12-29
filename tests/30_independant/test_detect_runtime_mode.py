# tests/0_independant/test_detect_runtime_mode.py
"""Tests for detect_runtime_mode() function.

The detect_runtime_mode() function checks multiple indicators to
determine how the code is currently running:
1. sys.frozen - PyInstaller/py2exe indicator
2. sys.modules["__main__"].__file__ ending with .pyz - zipapp indicator
3. __STITCHED__ in globals() - serger's stitched script indicator
4. Otherwise: package (default)

Note: The zipapp detection works by checking if the file specified by
the utils module's __file__ variable (as an attribute name on __main__)
ends with ".pyz". This is unusual but functional.
"""

import sys
from unittest.mock import MagicMock, patch

import apathetic_testing.runtime as amod_utils_runtime
from tests.utils import PROGRAM_PACKAGE


# --- convenience -----------------------------------------------------------

_runtime = amod_utils_runtime.ApatheticUtils_Internal_Runtime

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_detect_runtime_mode_frozen() -> None:
    """Test detection of PyInstaller/py2exe frozen mode.

    When sys.frozen is True, should return "frozen".
    """
    # --- setup ---
    with patch.object(sys, "frozen", True, create=True):
        # --- execute ---
        result = _runtime.detect_runtime_mode(PROGRAM_PACKAGE)

    # --- verify ---
    assert result == "frozen"


def test_detect_runtime_mode_zipapp() -> None:
    """Test detection of zipapp mode.

    A zipapp is a zipped Python application, typically ending in .pyz.
    The detection works by checking if the attribute named by utils.__file__
    on the __main__ module ends with ".pyz".

    For example, if utils.__file__ is "/path/to/utils.py", it checks:
    getattr(sys.modules["__main__"], "/path/to/utils.py", "").endswith(".pyz")

    In a real zipapp, __main__ might have an attribute with the zipapp path.
    For testing, we set the __main__ module attribute to a .pyz path.
    """
    # --- setup ---
    # Get the actual __file__ path from utils module
    utils_file = amod_utils_runtime.__file__
    assert utils_file is not None

    # Create a mock __main__ module
    mock_main = MagicMock()
    # Set the attribute that matches utils.__file__ to a .pyz path
    setattr(mock_main, utils_file, "/path/to/app.pyz")

    with (
        patch.object(sys, "frozen", False, create=True),
        patch.dict(sys.modules, {"__main__": mock_main}),
    ):
        # --- execute ---
        result = _runtime.detect_runtime_mode(PROGRAM_PACKAGE)

    # --- verify ---
    assert result == "zipapp"


def test_detect_runtime_mode_zipapp_complex_path() -> None:
    """Test zipapp detection with complex paths containing multiple separators."""
    # --- setup ---
    utils_file = amod_utils_runtime.__file__
    assert utils_file is not None

    mock_main = MagicMock()
    setattr(mock_main, utils_file, "/usr/local/bin/my-app.pyz")

    with (
        patch.object(sys, "frozen", False, create=True),
        patch.dict(sys.modules, {"__main__": mock_main}),
    ):
        # --- execute ---
        result = _runtime.detect_runtime_mode(PROGRAM_PACKAGE)

    # --- verify ---
    assert result == "zipapp"


def test_detect_runtime_mode_zipapp_missing_file_attribute() -> None:
    """When __main__ lacks the utils.__file__ attribute, should not match zipapp."""
    # --- setup ---
    # Create a mock __main__ without the utils.__file__ attribute
    mock_main = MagicMock(spec=[])  # spec=[] means no attributes

    # Save and remove serger module if it exists (it might have __STITCHED__)
    saved_serger = sys.modules.pop("serger", None)

    # Save and remove __STITCHED__/__STANDALONE__ from package module if it exists
    pkg_mod = sys.modules.get(PROGRAM_PACKAGE)
    saved_stitched = None
    saved_standalone = None
    if pkg_mod is not None:
        saved_stitched = getattr(pkg_mod, "__STITCHED__", None)
        saved_standalone = getattr(pkg_mod, "__STANDALONE__", None)
        if hasattr(pkg_mod, "__STITCHED__"):
            delattr(pkg_mod, "__STITCHED__")
        if hasattr(pkg_mod, "__STANDALONE__"):
            delattr(pkg_mod, "__STANDALONE__")

    try:
        with (
            patch.object(sys, "frozen", False, create=True),
            patch.dict(sys.modules, {"__main__": mock_main}),
            patch.dict(
                _runtime.detect_runtime_mode.__globals__,
                clear=False,
            ) as patched_globals,
        ):
            patched_globals.pop("__STITCHED__", None)
            patched_globals.pop("__STANDALONE__", None)
            # Ensure __main__ doesn't have __STITCHED__ either
            if hasattr(mock_main, "__STITCHED__"):
                delattr(mock_main, "__STITCHED__")
            if hasattr(mock_main, "__STANDALONE__"):
                delattr(mock_main, "__STANDALONE__")

            # --- execute ---
            result = _runtime.detect_runtime_mode(PROGRAM_PACKAGE)

        # --- verify ---
        # Should fall through to package since no indicators match
        assert result == "package"
    finally:
        # Restore package module attributes if they were there
        if pkg_mod is not None:
            if saved_stitched is not None:
                setattr(pkg_mod, "__STITCHED__", saved_stitched)  # noqa: B010
            if saved_standalone is not None:
                setattr(pkg_mod, "__STANDALONE__", saved_standalone)  # noqa: B010
        # Restore serger module if it was there
        if saved_serger is not None:
            sys.modules["serger"] = saved_serger


def test_detect_runtime_mode_stitched() -> None:
    """Test detection of stitched mode.

    serger's stitched script has __STITCHED__ in globals().
    """
    # --- setup ---
    # Create a context where frozen=False and the zipapp check fails
    utils_file = amod_utils_runtime.__file__
    assert utils_file is not None

    mock_main = MagicMock(spec=[])  # No attributes, so zipapp check fails

    with (
        patch.object(sys, "frozen", False, create=True),
        patch.dict(sys.modules, {"__main__": mock_main}),
        patch.dict(
            _runtime.detect_runtime_mode.__globals__,
            {"__STITCHED__": True},
            clear=False,
        ),
    ):
        # --- execute ---
        result = _runtime.detect_runtime_mode(PROGRAM_PACKAGE)

    # --- verify ---
    assert result == "stitched"


def test_detect_runtime_mode_package() -> None:
    """Test detection of package mode (default).

    When no other indicators are present, should return "package".
    """
    # --- setup ---
    # Create a mock __main__ that doesn't have the zipapp attribute
    mock_main = MagicMock(spec=[])

    # Save and remove serger module if it exists (it might have __STITCHED__)
    saved_serger = sys.modules.pop("serger", None)

    # Save and remove __STITCHED__/__STANDALONE__ from package module if it exists
    pkg_mod = sys.modules.get(PROGRAM_PACKAGE)
    saved_stitched = None
    saved_standalone = None
    if pkg_mod is not None:
        saved_stitched = getattr(pkg_mod, "__STITCHED__", None)
        saved_standalone = getattr(pkg_mod, "__STANDALONE__", None)
        if hasattr(pkg_mod, "__STITCHED__"):
            delattr(pkg_mod, "__STITCHED__")
        if hasattr(pkg_mod, "__STANDALONE__"):
            delattr(pkg_mod, "__STANDALONE__")

    try:
        with (
            patch.object(sys, "frozen", False, create=True),
            patch.dict(sys.modules, {"__main__": mock_main}),
            patch.dict(
                _runtime.detect_runtime_mode.__globals__,
                clear=False,
            ) as patched_globals,
        ):
            # Remove __STITCHED__ if it exists
            patched_globals.pop("__STITCHED__", None)
            patched_globals.pop("__STANDALONE__", None)
            # Ensure __main__ doesn't have __STITCHED__ either
            if hasattr(mock_main, "__STITCHED__"):
                delattr(mock_main, "__STITCHED__")
            if hasattr(mock_main, "__STANDALONE__"):
                delattr(mock_main, "__STANDALONE__")

            # --- execute ---
            result = _runtime.detect_runtime_mode(PROGRAM_PACKAGE)

        # --- verify ---
        assert result == "package"
    finally:
        # Restore package module attributes if they were there
        if pkg_mod is not None:
            if saved_stitched is not None:
                setattr(pkg_mod, "__STITCHED__", saved_stitched)  # noqa: B010
            if saved_standalone is not None:
                setattr(pkg_mod, "__STANDALONE__", saved_standalone)  # noqa: B010
        # Restore serger module if it was there
        if saved_serger is not None:
            sys.modules["serger"] = saved_serger


def test_detect_runtime_mode_package_missing_main() -> None:
    """Test package mode when __main__ is missing from sys.modules.

    This shouldn't normally happen in Python, but we should handle it.
    """
    # --- setup ---
    # Save and remove serger module if it exists (it might have __STITCHED__)
    saved_serger = sys.modules.pop("serger", None)

    # Save and remove __STITCHED__/__STANDALONE__ from package module if it exists
    pkg_mod = sys.modules.get(PROGRAM_PACKAGE)
    saved_stitched = None
    saved_standalone = None
    if pkg_mod is not None:
        saved_stitched = getattr(pkg_mod, "__STITCHED__", None)
        saved_standalone = getattr(pkg_mod, "__STANDALONE__", None)
        if hasattr(pkg_mod, "__STITCHED__"):
            delattr(pkg_mod, "__STITCHED__")
        if hasattr(pkg_mod, "__STANDALONE__"):
            delattr(pkg_mod, "__STANDALONE__")

    try:
        with (
            patch.object(sys, "frozen", False, create=True),
            patch.dict(sys.modules, {}, clear=False),
        ):  # Remove __main__ if present
            # Ensure __main__ is not in sys.modules for this test
            saved_main = sys.modules.pop("__main__", None)
            try:
                # Ensure __STITCHED__ is not in globals
                with patch.dict(
                    _runtime.detect_runtime_mode.__globals__,
                    clear=False,
                ) as patched_globals:
                    patched_globals.pop("__STITCHED__", None)
                    patched_globals.pop("__STANDALONE__", None)

                    # --- execute ---
                    result = _runtime.detect_runtime_mode(PROGRAM_PACKAGE)
            finally:
                # Restore __main__ if it was there
                if saved_main is not None:
                    sys.modules["__main__"] = saved_main

        # --- verify ---
        assert result == "package"
    finally:
        # Restore package module attributes if they were there
        if pkg_mod is not None:
            if saved_stitched is not None:
                setattr(pkg_mod, "__STITCHED__", saved_stitched)  # noqa: B010
            if saved_standalone is not None:
                setattr(pkg_mod, "__STANDALONE__", saved_standalone)  # noqa: B010
        # Restore serger module if it was there
        if saved_serger is not None:
            sys.modules["serger"] = saved_serger


def test_detect_runtime_mode_frozen_takes_precedence() -> None:
    """Test that frozen mode takes precedence over other indicators.

    Even if the zipapp or __STITCHED__ indicators match, if sys.frozen
    is True, it should return "frozen".
    """
    # --- setup ---
    utils_file = amod_utils_runtime.__file__
    assert utils_file is not None

    mock_main = MagicMock()
    setattr(mock_main, utils_file, "/path/to/app.pyz")

    with (
        patch.object(sys, "frozen", True, create=True),
        patch.dict(sys.modules, {"__main__": mock_main}),
        patch.dict(
            _runtime.detect_runtime_mode.__globals__,
            {"__STITCHED__": True},
            clear=False,
        ),
    ):
        # --- execute ---
        result = _runtime.detect_runtime_mode(PROGRAM_PACKAGE)

    # --- verify ---
    assert result == "frozen"


def test_detect_runtime_mode_zipapp_takes_precedence_over_stitched() -> None:
    """Test that zipapp detection takes precedence over stitched.

    If the zipapp check matches, it should return "zipapp" even if
    __STITCHED__ exists.
    """
    # --- setup ---
    utils_file = amod_utils_runtime.__file__
    assert utils_file is not None

    mock_main = MagicMock()
    setattr(mock_main, utils_file, "/path/to/app.pyz")

    with (
        patch.object(sys, "frozen", False, create=True),
        patch.dict(sys.modules, {"__main__": mock_main}),
        patch.dict(
            _runtime.detect_runtime_mode.__globals__,
            {"__STITCHED__": True},
            clear=False,
        ),
    ):
        # --- execute ---
        result = _runtime.detect_runtime_mode(PROGRAM_PACKAGE)

    # --- verify ---
    assert result == "zipapp"
