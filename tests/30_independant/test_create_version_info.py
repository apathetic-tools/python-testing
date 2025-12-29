# tests/30_independant/test_create_version_info.py
"""Tests for create_version_info utility function."""

import apathetic_testing as mod_autils


def test_create_version_info_basic() -> None:
    """create_version_info() should create a version_info-like object."""
    # --- execute ---
    version = mod_autils.create_version_info(3, 11)

    # --- verify ---
    assert version.major == 3  # noqa: PLR2004
    assert version.minor == 11  # noqa: PLR2004
    assert version.micro == 0
    assert version.releaselevel == "final"
    assert version.serial == 0


def test_create_version_info_with_micro() -> None:
    """create_version_info() should accept micro version."""
    # --- execute ---
    version = mod_autils.create_version_info(3, 11, 5)

    # --- verify ---
    assert version.major == 3  # noqa: PLR2004
    assert version.minor == 11  # noqa: PLR2004
    assert version.micro == 5  # noqa: PLR2004


def test_create_version_info_tuple_comparison() -> None:
    """create_version_info() should support tuple comparison like sys.version_info."""
    # --- setup ---
    version = mod_autils.create_version_info(3, 11)

    # --- execute and verify ---
    assert version >= (3, 10)
    assert version >= (3, 11)
    assert not version >= (3, 12)
    assert version < (3, 12)
    assert version > (3, 10)


def test_create_version_info_tuple_access() -> None:
    """create_version_info() should support tuple-like access."""
    # --- setup ---
    version = mod_autils.create_version_info(3, 11, 2)

    # --- execute and verify ---
    assert version[0] == 3  # noqa: PLR2004
    assert version[1] == 11  # noqa: PLR2004
    assert version[2] == 2  # noqa: PLR2004
    assert version[3] == "final"
    assert version[4] == 0


def test_create_version_info_named_tuple_behavior() -> None:
    """create_version_info() should behave like a NamedTuple."""
    # --- setup ---
    version = mod_autils.create_version_info(3, 11)

    # --- execute and verify ---
    # Should support both attribute and index access
    assert version.major == version[0]
    assert version.minor == version[1]
    assert version.micro == version[2]
    assert version.releaselevel == version[3]
    assert version.serial == version[4]


def test_create_version_info_named_tuple_type() -> None:
    """create_version_info() should return a NamedTuple instance."""
    # --- execute ---
    # This test ensures the class definition (lines 48-55) and return
    # (lines 57-59) are covered
    version = mod_autils.create_version_info(2, 7, 3)

    # --- verify ---
    # Verify it's a tuple-like object
    assert isinstance(version, tuple)
    # Verify all NamedTuple fields are accessible
    assert hasattr(version, "major")  # pyright: ignore[reportUnknownArgumentType]
    assert hasattr(version, "minor")  # pyright: ignore[reportUnknownArgumentType]
    assert hasattr(version, "micro")  # pyright: ignore[reportUnknownArgumentType]
    assert hasattr(version, "releaselevel")  # pyright: ignore[reportUnknownArgumentType]
    assert hasattr(version, "serial")  # pyright: ignore[reportUnknownArgumentType]
    # Verify the values match what we passed
    assert version.major == 2  # noqa: PLR2004  # pyright: ignore[reportUnknownMemberType,reportAttributeAccessIssue]
    assert version.minor == 7  # noqa: PLR2004  # pyright: ignore[reportUnknownMemberType,reportAttributeAccessIssue]
    assert version.micro == 3  # noqa: PLR2004  # pyright: ignore[reportUnknownMemberType,reportAttributeAccessIssue]
    assert version.releaselevel == "final"  # pyright: ignore[reportUnknownMemberType,reportAttributeAccessIssue]
    assert version.serial == 0  # pyright: ignore[reportUnknownMemberType,reportAttributeAccessIssue]
    # Verify it can be unpacked like a tuple
    major, minor, micro, releaselevel, serial = version  # pyright: ignore[reportUnknownVariableType]
    assert major == 2  # noqa: PLR2004
    assert minor == 7  # noqa: PLR2004
    assert micro == 3  # noqa: PLR2004
    assert releaselevel == "final"
    assert serial == 0
