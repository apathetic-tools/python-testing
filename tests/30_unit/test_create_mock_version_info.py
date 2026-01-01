"""Unit tests for create_mock_version_info function."""

import apathetic_testing.mock as mod_mock


# Test constants
MAJOR_VERSION = 3
MINOR_VERSION_A = 11
MINOR_VERSION_B = 10
MINOR_VERSION_C = 9
MICRO_VERSION = 5
MICRO_DEFAULT = 0
SERIAL_DEFAULT = 0


def test_create_mock_version_info_basic() -> None:
    """Test creating a basic mock version_info with major and minor."""
    version_info = mod_mock.ApatheticTest_Internal_Mock.create_mock_version_info(
        major=MAJOR_VERSION, minor=MINOR_VERSION_A
    )

    assert version_info.major == MAJOR_VERSION
    assert version_info.minor == MINOR_VERSION_A
    assert version_info.micro == MICRO_DEFAULT
    assert version_info.releaselevel == "final"
    assert version_info.serial == SERIAL_DEFAULT


def test_create_mock_version_info_with_micro() -> None:
    """Test creating a mock version_info with explicit micro version."""
    version_info = mod_mock.ApatheticTest_Internal_Mock.create_mock_version_info(
        major=MAJOR_VERSION, minor=MINOR_VERSION_B, micro=MICRO_VERSION
    )

    assert version_info.major == MAJOR_VERSION
    assert version_info.minor == MINOR_VERSION_B
    assert version_info.micro == MICRO_VERSION
    assert version_info.releaselevel == "final"
    assert version_info.serial == SERIAL_DEFAULT


def test_create_mock_version_info_tuple_like() -> None:
    """Test that mock version_info supports tuple-like access."""
    version_info = mod_mock.ApatheticTest_Internal_Mock.create_mock_version_info(
        major=MAJOR_VERSION, minor=MINOR_VERSION_C
    )

    # Named tuples support indexing
    assert version_info[0] == MAJOR_VERSION  # major
    assert version_info[1] == MINOR_VERSION_C  # minor
    assert version_info[2] == MICRO_DEFAULT  # micro
