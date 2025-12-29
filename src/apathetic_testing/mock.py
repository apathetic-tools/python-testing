# src/apathetic_testing/mock.py
"""Mock utilities mixin for testing mixin methods."""

from __future__ import annotations

import sys
from contextlib import suppress
from typing import Any
from unittest.mock import MagicMock

import pytest


class ApatheticTest_Internal_Mock:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class providing mock-related utilities."""

    @staticmethod
    def create_mock_superclass_test(
        mixin_class: type,
        parent_class: type,
        method_name: str,
        camel_case_method_name: str,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test that a mixin's snake_case method calls parent's camelCase via super().

        Creates a test class with controlled MRO:
        - TestClass inherits from mixin_class, then MockBaseClass
        - MockBaseClass provides the camelCase method that super() resolves to
        - Mocks the camelCase method and verifies it's called

        Args:
            mixin_class: The mixin class containing the snake_case method
            parent_class: The parent class with the camelCase method
                (e.g., logging.Logger)
            method_name: Name of the snake_case method to test (e.g., "add_filter")
            camel_case_method_name: Name of the camelCase method to mock
                (e.g., "addFilter")
            args: Arguments to pass to the snake_case method
            kwargs: Keyword arguments to pass to the snake_case method
            monkeypatch: pytest.MonkeyPatch fixture for patching

        Raises:
            AssertionError: If the camelCase method was not called as expected
        """
        # Get the real camelCase method from parent class to use as the base
        # implementation. Check if the method exists first.
        if not hasattr(parent_class, camel_case_method_name):
            py_version = f"{sys.version_info[0]}.{sys.version_info[1]}"
            pytest.skip(
                f"{camel_case_method_name} does not exist on {parent_class.__name__} "
                f"(Python {py_version})"
            )
        camel_method_unbound = getattr(parent_class, camel_case_method_name)

        # Create a base class with the camelCase method (what super() resolves to)
        # We define it dynamically so we can use any method name
        # The method needs to exist on the class for patching to work
        def create_method(camel_method: Any) -> Any:
            """Create a method that wraps the parent class method."""

            def method(self: Any, *a: Any, **kw: Any) -> Any:
                return camel_method(self, *a, **kw)

            return method

        mock_base_class = type(
            "MockBaseClass",
            (),
            {camel_case_method_name: create_method(camel_method_unbound)},
        )

        # Create test class: mixin first, then base class
        # MRO: TestLogger -> Mixin -> MockBaseClass -> object
        # When super() is called from Mixin, it resolves to MockBaseClass
        class TestClass(mixin_class, mock_base_class):  # type: ignore[misc, valid-type]
            """Test class with controlled MRO for super() resolution."""

            def __init__(self) -> None:
                mock_base_class.__init__(self)  # type: ignore[misc]

        # Create an instance of our test class
        test_instance = TestClass()

        # Get the snake_case method from the test instance
        snake_method = getattr(test_instance, method_name)
        if snake_method is None:
            msg = f"Method {method_name} not found on {mixin_class.__name__}"
            raise AttributeError(msg)

        # Mock the base class method (what super() resolves to)
        mock_method = MagicMock(wraps=camel_method_unbound)
        monkeypatch.setattr(mock_base_class, camel_case_method_name, mock_method)
        # Call the snake_case method on our test instance
        # Some methods may raise (e.g., invalid arguments)
        # That's okay - we just want to verify the mock was called
        with suppress(Exception):
            snake_method(*args, **kwargs)

        # Verify the underlying method was called
        # For super() calls, this verifies the parent method was invoked
        # When called via super(), the method is bound, so self is implicit
        # The mock receives just the args (self is already bound)
        # This is a "happy path" test - we just verify the method was called
        # (exact argument matching is less important than verifying the call happened)
        if not mock_method.called:
            msg = f"{camel_case_method_name} was not called by {method_name}"
            raise AssertionError(msg)
        # If we have simple args/kwargs, try to verify them more precisely
        # But don't fail if the method has defaults that fill in extra args
        if args and not kwargs:
            # For positional-only calls, check the first few args match
            call_args = mock_method.call_args
            if call_args:
                call_args_pos, _ = call_args
                # Verify at least the first arg matches (if we have args)
                if (
                    call_args_pos
                    and len(call_args_pos) >= len(args)
                    and call_args_pos[: len(args)] != args
                ):
                    msg = (
                        f"Args don't match: expected {args}, "
                        f"got {call_args_pos[: len(args)]}"
                    )
                    raise AssertionError(msg)
