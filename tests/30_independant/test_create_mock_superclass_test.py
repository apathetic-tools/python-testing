# we import '_' private for testing purposes only
# pyright: reportPrivateUsage=false
"""Tests for create_mock_superclass_test function."""

from __future__ import annotations

from typing import Any

import pytest

import apathetic_testing as mod_apathetic_testing


class SimpleMixin:
    """Simple mixin class for testing super() call verification."""

    def add_item(self, item: str) -> None:
        """Add an item via super()."""
        super().addItem(item)  # type: ignore[misc]

    def set_count(self, count: int, *, label: str = "") -> None:
        """Set count via super() with keyword args."""
        super().setCount(count, label=label)  # type: ignore[misc]


def test_create_mock_superclass_test_verifies_super_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that super() is called correctly from mixin method."""
    # This tests the happy path: mixin calls parent via super()

    # Create a mock parent class with the camelCase method
    class MockParent:
        def addItem(self, item: str) -> None:  # noqa: N802
            pass

    # --- execute ---
    # Call create_mock_superclass_test with the mixin and parent
    mod_apathetic_testing.create_mock_superclass_test(
        mixin_class=SimpleMixin,
        parent_class=MockParent,
        method_name="add_item",
        camel_case_method_name="addItem",
        args=("test_item",),
        kwargs={},
        monkeypatch=monkeypatch,
    )
    # If we reach here without an exception, the test passed


def test_create_mock_superclass_test_with_kwargs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify super() call with keyword arguments."""
    # This tests that kwargs are handled correctly

    class MockParentWithKwargs:
        def setCount(self, count: int, label: str = "") -> None:  # noqa: N802
            pass

    # --- execute ---
    # Test with both positional and keyword arguments
    mod_apathetic_testing.create_mock_superclass_test(
        mixin_class=SimpleMixin,
        parent_class=MockParentWithKwargs,
        method_name="set_count",
        camel_case_method_name="setCount",
        args=(42,),
        kwargs={"label": "test"},
        monkeypatch=monkeypatch,
    )


def test_create_mock_superclass_test_method_not_found_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Raise AssertionError if method is not called."""
    # This tests the error case: mixin method doesn't call parent via super()

    class BrokenMixin:
        """Mixin that doesn't call super()."""

        def add_item(self, item: str) -> None:
            # Missing super() call!
            pass

    class MockParent:
        def addItem(self, item: str) -> None:  # noqa: N802
            pass

    # --- execute & verify ---
    with pytest.raises(AssertionError, match="addItem was not called by add_item"):
        mod_apathetic_testing.create_mock_superclass_test(
            mixin_class=BrokenMixin,
            parent_class=MockParent,
            method_name="add_item",
            camel_case_method_name="addItem",
            args=("test_item",),
            kwargs={},
            monkeypatch=monkeypatch,
        )


def test_create_mock_superclass_test_missing_method_on_mixin_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Raise AttributeError if mixin doesn't have the method."""
    # This tests the error case: mixin doesn't have the snake_case method

    class EmptyMixin:
        """Mixin with no methods."""

    class MockParent:
        def addItem(self, item: str) -> None:  # noqa: N802
            pass

    # --- execute & verify ---
    with pytest.raises(AttributeError, match="has no attribute 'add_item'"):
        mod_apathetic_testing.create_mock_superclass_test(
            mixin_class=EmptyMixin,
            parent_class=MockParent,
            method_name="add_item",
            camel_case_method_name="addItem",
            args=("test_item",),
            kwargs={},
            monkeypatch=monkeypatch,
        )


def test_create_mock_superclass_test_missing_camel_case_method_skips(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Skip if parent class doesn't have the camelCase method."""
    # This tests skipping when method doesn't exist on parent

    class MockParentWithoutMethod:
        pass

    # --- execute & verify ---
    # pytest.skip raises a special Skip exception
    with pytest.raises(pytest.skip.Exception):
        mod_apathetic_testing.create_mock_superclass_test(
            mixin_class=SimpleMixin,
            parent_class=MockParentWithoutMethod,
            method_name="add_item",
            camel_case_method_name="addItem",
            args=("test_item",),
            kwargs={},
            monkeypatch=monkeypatch,
        )


def test_create_mock_superclass_test_missing_camel_case_method_with_marker(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that skipping behavior works correctly when method missing."""
    # Use pytest.mark.xfail to handle the skip in a more direct way

    class MockParentWithoutMethod:
        pass

    # --- execute ---
    # This should result in a skip
    try:
        mod_apathetic_testing.create_mock_superclass_test(
            mixin_class=SimpleMixin,
            parent_class=MockParentWithoutMethod,
            method_name="add_item",
            camel_case_method_name="addItem",
            args=("test_item",),
            kwargs={},
            monkeypatch=monkeypatch,
        )
        # If we get here, the skip didn't happen
        pytest.fail("Expected pytest.skip to be called")
    except pytest.skip.Exception:
        # This is the expected behavior
        pass


def test_create_mock_superclass_test_with_no_args(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify super() call with no arguments."""
    # This tests that empty args/kwargs are handled correctly

    class NoArgsMixin:
        """Mixin method with no arguments."""

        def initialize(self) -> None:
            """Initialize via super()."""
            super().initialize()  # type: ignore[misc]

    class NoArgsParent:
        def initialize(self) -> None:
            pass

    # --- execute ---
    mod_apathetic_testing.create_mock_superclass_test(
        mixin_class=NoArgsMixin,
        parent_class=NoArgsParent,
        method_name="initialize",
        camel_case_method_name="initialize",
        args=(),
        kwargs={},
        monkeypatch=monkeypatch,
    )


def test_create_mock_superclass_test_with_multiple_args(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify super() call with multiple positional arguments."""
    # This tests that multiple args are passed through correctly

    class MultiArgMixin:
        """Mixin with multiple arguments."""

        def process(self, a: Any, b: Any, c: Any) -> None:
            """Process with multiple args via super()."""
            super().process(a, b, c)  # type: ignore[misc]

    class MultiArgParent:
        def process(self, a: Any, b: Any, c: Any) -> None:
            pass

    # --- execute ---
    mod_apathetic_testing.create_mock_superclass_test(
        mixin_class=MultiArgMixin,
        parent_class=MultiArgParent,
        method_name="process",
        camel_case_method_name="process",
        args=("first", 42, [1, 2, 3]),
        kwargs={},
        monkeypatch=monkeypatch,
    )
