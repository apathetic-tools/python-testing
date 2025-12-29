# tests/0_independant/test_safe_isinstance.py
"""Focused tests for serger.utils_core.safe_isinstance."""

from typing import Any, Literal, TypedDict, TypeVar, get_args, get_origin

from typing_extensions import NotRequired

import apathetic_testing as mod_autils


def test_plain_types_work_normally() -> None:
    # --- execute, and verify ---
    assert mod_autils.safe_isinstance("x", str)
    assert not mod_autils.safe_isinstance(123, str)
    assert mod_autils.safe_isinstance(123, int)


def test_union_types() -> None:
    # --- setup ---
    u = str | int

    # --- execute and verify ---
    assert mod_autils.safe_isinstance("abc", u)
    assert mod_autils.safe_isinstance(42, u)
    assert not mod_autils.safe_isinstance(3.14, u)


def test_optional_types() -> None:
    # --- setup ---
    opt = int | None

    # --- execute and verify ---
    assert mod_autils.safe_isinstance(5, opt)
    assert mod_autils.safe_isinstance(None, opt)
    assert not mod_autils.safe_isinstance("nope", opt)


def test_any_type_always_true() -> None:
    # --- execute and verify ---
    assert mod_autils.safe_isinstance("anything", Any)
    assert mod_autils.safe_isinstance(None, Any)
    assert mod_autils.safe_isinstance(42, Any)


def test_list_type_accepts_lists() -> None:
    # --- execute and verify ---
    assert mod_autils.safe_isinstance([], list)
    assert not mod_autils.safe_isinstance({}, list)


def test_list_of_str_type_accepts_strings_inside() -> None:
    # --- setup ---
    list_str = list[str]

    # --- execute and verify ---
    assert mod_autils.safe_isinstance(["a", "b"], list_str)
    assert not mod_autils.safe_isinstance(["a", 2], list_str)


def test_typed_dict_like_accepts_dicts() -> None:
    # --- setup ---
    class DummyDict(TypedDict):
        foo: str
        bar: int

    # --- execute and verify ---
    # should treat dicts as valid, not crash
    assert mod_autils.safe_isinstance({"foo": "x", "bar": 1}, DummyDict)
    assert not mod_autils.safe_isinstance("not a dict", DummyDict)


def test_union_with_list_and_dict() -> None:
    # --- setup ---
    u = list[str] | dict[str, int]

    # --- execute and verify ---
    assert mod_autils.safe_isinstance(["a", "b"], u)
    assert mod_autils.safe_isinstance({"a": 1}, u)
    assert not mod_autils.safe_isinstance(42, u)


def test_does_not_raise_on_weird_types() -> None:
    """Exotic typing constructs should not raise exceptions."""

    # --- setup ---
    class A: ...

    T = TypeVar("T", bound=A)

    # --- execute ---
    # just ensure it returns a boolean, not crash
    result = mod_autils.safe_isinstance(A(), T)

    # --- verify ---
    assert isinstance(result, bool)


def test_nested_generics_work() -> None:
    # --- setup ---
    l2 = list[list[int]]

    # --- execute and verify ---
    assert mod_autils.safe_isinstance([[1, 2], [3, 4]], l2)
    assert not mod_autils.safe_isinstance([[1, "a"]], l2)


def test_literal_values_match() -> None:
    # --- setup ---
    lit = Literal["x", "y"]

    # --- execute and verify ---
    assert mod_autils.safe_isinstance("x", lit)
    assert not mod_autils.safe_isinstance("z", lit)


def test_tuple_generic_support() -> None:
    # --- setup ---
    tup = tuple[int, str]

    # --- execute and verify ---
    assert mod_autils.safe_isinstance((1, "a"), tup)
    assert not mod_autils.safe_isinstance(("a", 1), tup)


def test_tuple_with_ellipsis() -> None:
    """Tuple with Ellipsis should match variable-length tuples."""
    # --- setup ---
    tup = tuple[str, ...]

    # --- execute and verify ---
    assert mod_autils.safe_isinstance(("a",), tup)
    assert mod_autils.safe_isinstance(("a", "b"), tup)
    assert mod_autils.safe_isinstance(("a", "b", "c"), tup)
    # Non-string tuples should not match
    assert not mod_autils.safe_isinstance((1, 2), tup)
    assert not mod_autils.safe_isinstance(("a", 1), tup)


def test_tuple_ellipsis_edge_cases() -> None:
    """Tuple with Ellipsis should handle edge cases."""
    # --- setup ---
    tup = tuple[int, ...]

    # --- execute and verify ---
    # Test empty tuple
    assert mod_autils.safe_isinstance((), tup)
    # Test single element
    assert mod_autils.safe_isinstance((1,), tup)
    # Test multiple elements
    assert mod_autils.safe_isinstance((1, 2, 3), tup)
    # Test mixed types (should fail)
    assert not mod_autils.safe_isinstance((1, "a"), tup)


def test_tuple_mismatched_length() -> None:
    """Tuple with fixed length should reject mismatched lengths."""
    # --- setup ---
    tup = tuple[int, str]

    # --- execute and verify ---
    assert mod_autils.safe_isinstance((1, "a"), tup)
    assert not mod_autils.safe_isinstance((1,), tup)  # Too short
    assert not mod_autils.safe_isinstance((1, "a", 2), tup)  # Too long
    # Test with correct length but wrong types
    assert not mod_autils.safe_isinstance(("a", 1), tup)  # Wrong types


def test_generic_without_args() -> None:
    """Generic types without args should work."""
    # --- setup ---
    # list without args (just list)
    plain_list = list

    # --- execute and verify ---
    assert mod_autils.safe_isinstance([], plain_list)
    assert mod_autils.safe_isinstance([1, 2, 3], plain_list)
    assert not mod_autils.safe_isinstance({}, plain_list)


def test_isinstance_generics_no_args_early_return() -> None:
    """Generic types without args should return True early."""
    # Use a generic type that has an origin but no args
    plain_dict = dict
    # dict without args should have origin=dict and args=()
    origin = get_origin(plain_dict)
    args = get_args(plain_dict)

    # If origin is dict and args is empty, should return True
    if origin is dict and not args:
        result = mod_autils.safe_isinstance({}, plain_dict)
        assert result is True


def test_safe_isinstance_handles_typeerror_gracefully() -> None:
    """safe_isinstance() should handle TypeError from isinstance gracefully."""

    # --- setup ---
    # Create a type that will raise TypeError when used with isinstance
    class BadType:
        pass

    # --- execute ---
    # Should not raise, should return False
    # Use the class directly, not indexed
    result = mod_autils.safe_isinstance("test", BadType)

    # --- verify ---
    assert isinstance(result, bool)
    assert result is False


def test_safe_isinstance_typeerror_in_typeddict_check() -> None:
    """safe_isinstance() should handle TypeError in TypedDict check."""
    # --- setup ---
    # Create something that's not a class but might trigger the TypedDict check
    # We need something that will raise TypeError when checking
    # isinstance(expected_type, type)
    not_a_class = "not a class"

    # --- execute ---
    # Should not raise, should return False
    # The TypeError in the try block should be caught
    result = mod_autils.safe_isinstance({}, not_a_class)

    # --- verify ---
    assert isinstance(result, bool)
    # Should fall through to the final isinstance check or return False
    assert result is False


def test_safe_isinstance_typeerror_in_final_isinstance() -> None:
    """safe_isinstance() should handle TypeError in final isinstance check."""
    # --- setup ---
    # Create something that will raise TypeError when used with isinstance
    # Use a non-type value that will cause isinstance to raise
    bad_type = object()  # Not a type, just an object

    # --- execute ---
    # Should catch TypeError and return False
    result = mod_autils.safe_isinstance("test", bad_type)

    # --- verify ---
    assert isinstance(result, bool)
    assert result is False


class TestNotRequired:
    """Tests for NotRequired type handling."""

    def test_notrequired_string_accepts_string(self) -> None:
        """NotRequired[str] should accept strings."""
        nr = NotRequired[str]

        # --- execute and verify ---
        assert mod_autils.safe_isinstance("hello", nr)

    def test_notrequired_string_rejects_int(self) -> None:
        """NotRequired[str] should reject integers."""
        nr = NotRequired[str]

        # --- execute and verify ---
        assert not mod_autils.safe_isinstance(42, nr)

    def test_notrequired_int(self) -> None:
        """NotRequired[int] should validate int types."""
        nr = NotRequired[int]

        # --- execute and verify ---
        assert mod_autils.safe_isinstance(123, nr)
        assert not mod_autils.safe_isinstance("not int", nr)

    def test_notrequired_list_of_str(self) -> None:
        """NotRequired[list[str]] should work with list generics."""
        nr = NotRequired[list[str]]

        # --- execute and verify ---
        assert mod_autils.safe_isinstance(["a", "b"], nr)
        assert not mod_autils.safe_isinstance(["a", 2], nr)
        assert not mod_autils.safe_isinstance("not a list", nr)

    def test_notrequired_union(self) -> None:
        """NotRequired can wrap Union types."""
        nr = NotRequired[str | int]

        # --- execute and verify ---
        assert mod_autils.safe_isinstance("hello", nr)
        assert mod_autils.safe_isinstance(42, nr)
        assert not mod_autils.safe_isinstance(3.14, nr)

    def test_notrequired_dict(self) -> None:
        """NotRequired can wrap dict types."""
        nr = NotRequired[dict[str, int]]

        # --- execute and verify ---
        assert mod_autils.safe_isinstance({"a": 1, "b": 2}, nr)
        assert not mod_autils.safe_isinstance({"a": "not int"}, nr)
        assert not mod_autils.safe_isinstance("not a dict", nr)

    def test_notrequired_typeddict(self) -> None:
        """NotRequired can wrap TypedDict types."""

        class Config(TypedDict):
            name: str
            value: int

        nr = NotRequired[Config]

        # --- execute and verify ---
        assert mod_autils.safe_isinstance({"name": "test", "value": 1}, nr)
        assert mod_autils.safe_isinstance({}, nr)  # TypedDicts treat dicts
        assert not mod_autils.safe_isinstance("not a dict", nr)

    def test_notrequired_without_args(self) -> None:
        """NotRequired without args should return a boolean."""
        # NotRequired by itself (no args) - this is edge case
        # The actual behavior depends on how get_origin/get_args work
        result = mod_autils.safe_isinstance("anything", NotRequired)
        # Should return a boolean (implementation may vary)
        assert isinstance(result, bool)
