"""Integration tests for logging fixture workarounds against duplication bugs.

STRATEGY
--------
These tests validate that our logging fixtures properly work around known
duplication bugs in apathetic-logging. They verify the user-visible outcome:
log messages should appear exactly once, regardless of the underlying cause
(duplicate handlers, propagation loops, cache corruption, or other mechanisms).

WHY FIXTURE REGRESSION TESTS?
-----------------------------
The fixtures we provide (isolated_logging, logging_test_level, etc.) were
specifically designed to work around duplication bugs in apathetic-logging.
This module ensures those workarounds continue to work if apathetic-logging
changes in the future.

These tests:
- Validate that our fixture isolation prevents message duplication
- Detect if apathetic-logging reintroduces duplication bugs
- Act as regression tests for the bugs our fixtures were designed to prevent

SYMPTOM-BASED APPROACH
----------------------
Message duplication can be introduced by many different root causes:
- Handler duplication (same handler registered multiple times)
- Propagation loops (messages propagating through multiple paths)
- Cache state corruption (stream IDs causing re-entry)
- Registry inconsistencies
- And potentially other unknown causes discovered during refactoring

A symptom-based approach catches ANY duplication bug, not just ones we
anticipate. This provides defense-in-depth against regressions.

PARALLEL EXECUTION NOTE
------------------------
These tests use the capture_streams() context manager from our isolated_logging
fixture. This approach works reliably in:
- Serial mode (pytest without xdist)
- Parallel mode (pytest-xdist with multiple workers)
- Package mode (src/ imports)
- Stitched mode (dist/ single-file)
- Zipapp mode (dist/ .pyz bundle)

This avoids caplog's worker process inconsistencies and handler identity
issues in stitched mode.

Related: test_logging_fixture_regression__sequential_bug.py (mechanism-specific tests)
"""

from __future__ import annotations

import logging
from typing import Any

import apathetic_logging as amod_logging


# Maximum handlers allowed before we suspect duplication
MAX_HANDLERS_REASONABLE = 3


def test_child_propagates_without_excessive_duplication(
    isolated_logging: Any,
) -> None:
    """Verify child logger message appears without excessive duplication.

    Uses manual stream capture to count log records. Checks that when a child logger
    propagates to root, messages aren't duplicated excessively (e.g.,
    14-17 times like the duplication bug).
    """
    root = logging.getLogger("")
    child = logging.getLogger("child_propagate_test")

    root.setLevel(logging.DEBUG)
    child.setLevel(logging.DEBUG)
    child.propagate = True

    # Capture output with stream capture
    with isolated_logging.capture_streams() as capture:
        child.debug("UNIQUE_CHILD_PROPAGATE_001")

    # Count message appearances in output
    count = capture.count_message("UNIQUE_CHILD_PROPAGATE_001")

    # Should appear exactly 1 time, not 14-17 (the bug)
    assert count == 1, (
        f"Expected message once, got {count} times. This indicates duplication."
    )


def test_root_and_child_logging_no_excessive_duplication(
    isolated_logging: Any,
) -> None:
    """Verify separate messages from root and child don't duplicate excessively."""
    root = logging.getLogger("")
    child = logging.getLogger("child_separate_test")

    root.setLevel(logging.DEBUG)
    child.setLevel(logging.DEBUG)
    child.propagate = True

    # Capture output with stream capture
    with isolated_logging.capture_streams() as capture:
        root.debug("UNIQUE_ROOT_MESSAGE_002")
        child.debug("UNIQUE_CHILD_MESSAGE_002")

    # Each should appear exactly once
    root_count = capture.count_message("UNIQUE_ROOT_MESSAGE_002")
    child_count = capture.count_message("UNIQUE_CHILD_MESSAGE_002")

    assert root_count == 1, (
        f"Root message appeared {root_count} times (expected 1). Duplication detected."
    )
    assert child_count == 1, (
        f"Child message appeared {child_count} times (expected 1). "
        "Duplication detected."
    )


def test_multiple_children_no_excessive_duplication(
    isolated_logging: Any,
) -> None:
    """Verify multiple child loggers propagate without excessive duplication."""
    root = logging.getLogger("")
    child1 = logging.getLogger("child_multi_1")
    child2 = logging.getLogger("child_multi_2")
    child3 = logging.getLogger("child_multi_3")

    root.setLevel(logging.DEBUG)
    for child in [child1, child2, child3]:
        child.setLevel(logging.DEBUG)
        child.propagate = True

    # Capture output with stream capture
    with isolated_logging.capture_streams() as capture:
        child1.debug("UNIQUE_MULTI_MSG_1_003")
        child2.debug("UNIQUE_MULTI_MSG_2_003")
        child3.debug("UNIQUE_MULTI_MSG_3_003")

    # Each should appear exactly once
    for i, msg in enumerate(
        [
            "UNIQUE_MULTI_MSG_1_003",
            "UNIQUE_MULTI_MSG_2_003",
            "UNIQUE_MULTI_MSG_3_003",
        ],
        1,
    ):
        count = capture.count_message(msg)
        assert count == 1, (
            f"Message {i} appeared {count} times (expected 1). Duplication detected."
        )


def test_sequential_messages_no_excessive_duplication(
    isolated_logging: Any,
) -> None:
    """Verify sequential logging doesn't cause excessive duplication."""
    root = logging.getLogger("")
    logger = logging.getLogger("sequential_test")

    root.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    logger.propagate = True

    # Capture output with stream capture
    with isolated_logging.capture_streams() as capture:
        for i in range(1, 6):
            logger.debug("UNIQUE_SEQ_MSG_%d_004", i)

    # Each should appear exactly once
    for i in range(1, 6):
        msg = f"UNIQUE_SEQ_MSG_{i}_004"
        count = capture.count_message(msg)
        assert count == 1, (
            f"Sequential message {i} appeared {count} times (expected 1). "
            "Duplication or bleed detected."
        )


def test_non_propagating_child_no_excessive_duplication(
    isolated_logging: Any,  # noqa: ARG001
) -> None:
    """Verify non-propagating child logger doesn't have duplicate handlers.

    Non-propagating loggers get their own handler. This test verifies that
    when a non-propagating logger logs, it doesn't accumulate duplicate
    handlers (e.g., 14+ handlers like the duplication bug could cause).
    """
    root = logging.getLogger("")
    child = logging.getLogger("child_no_propagate_test")

    root.setLevel(logging.DEBUG)
    child.setLevel(logging.DEBUG)
    child.propagate = False

    # Log from non-propagating child to trigger handler creation
    child.debug("UNIQUE_NOPROP_MSG_005")

    # Non-propagating logger should have its own handler(s), but not excessively
    handler_count = len(child.handlers)
    assert handler_count > 0, (
        f"Non-propagating child should have handler, got {handler_count}."
    )
    assert handler_count <= MAX_HANDLERS_REASONABLE, (
        f"Non-propagating child has {handler_count} handlers "
        f"(expected ≤{MAX_HANDLERS_REASONABLE}). "
        "Handler duplication detected."
    )


def test_mixed_propagating_and_non_propagating_no_duplication(
    isolated_logging: Any,
) -> None:
    """Verify mix of propagating and non-propagating children works correctly."""
    root = logging.getLogger("")
    child_prop = logging.getLogger("mixed_propagate")
    child_no_prop = logging.getLogger("mixed_no_propagate")

    root.setLevel(logging.DEBUG)
    child_prop.setLevel(logging.DEBUG)
    child_prop.propagate = True

    child_no_prop.setLevel(logging.DEBUG)
    child_no_prop.propagate = False

    # Capture output with stream capture
    with isolated_logging.capture_streams() as capture:
        child_prop.debug("UNIQUE_PROP_MSG_XYZ_006")
        child_no_prop.debug("UNIQUE_NOPROP_MSG_ABC_006")

    # Check propagating message in output
    prop_count = capture.count_message("UNIQUE_PROP_MSG_XYZ_006")
    assert prop_count == 1, (
        f"Propagating message appeared {prop_count} times (expected 1)."
    )

    # Non-propagating logger should have reasonable handler count
    no_prop_handler_count = len(child_no_prop.handlers)
    assert no_prop_handler_count > 0, (
        f"Non-propagating child should have handler, got {no_prop_handler_count}."
    )
    assert no_prop_handler_count <= MAX_HANDLERS_REASONABLE, (
        f"Non-propagating child has {no_prop_handler_count} handlers "
        f"(expected ≤{MAX_HANDLERS_REASONABLE}). "
        "Handler duplication detected."
    )


def test_root_level_context_no_excessive_duplication(
    isolated_logging: Any,
) -> None:
    """Verify useRootLevel context doesn't cause excessive output duplication."""
    root = logging.getLogger("")
    child = logging.getLogger("context_test")

    child.propagate = True

    # Capture output with stream capture
    with (
        isolated_logging.capture_streams() as capture,
        amod_logging.useRootLevel("DEBUG"),
    ):
        root.debug("UNIQUE_CONTEXT_ROOT_MSG_007")
        child.debug("UNIQUE_CONTEXT_CHILD_MSG_007")

    # Each should appear exactly once
    root_count = capture.count_message("UNIQUE_CONTEXT_ROOT_MSG_007")
    child_count = capture.count_message("UNIQUE_CONTEXT_CHILD_MSG_007")

    assert root_count == 1, (
        f"Context root message appeared {root_count} times (expected 1). "
        "useRootLevel caused duplication."
    )
    assert child_count == 1, (
        f"Context child message appeared {child_count} times (expected 1). "
        "useRootLevel caused duplication."
    )


def test_sequential_root_level_contexts_no_excessive_duplication(
    isolated_logging: Any,
) -> None:
    """Verify sequential useRootLevel contexts don't cause excessive duplication.

    This is the critical test for the sequential bug (14-17x duplication).
    Ensures that sequential useRootLevel() calls don't cause messages to
    appear multiple times.
    """
    logger = logging.getLogger("sequential_context_test")
    logger.propagate = True

    # Use useRootLevel sequentially (reproduces the bug scenario)
    with (
        isolated_logging.capture_streams() as capture1,
        amod_logging.useRootLevel("DEBUG"),
    ):
        logger.debug("UNIQUE_SEQUENTIAL_CONTEXT_MSG_1_008")
    msg1_count = capture1.count_message("UNIQUE_SEQUENTIAL_CONTEXT_MSG_1_008")

    with (
        isolated_logging.capture_streams() as capture2,
        amod_logging.useRootLevel("DEBUG"),
    ):
        logger.debug("UNIQUE_SEQUENTIAL_CONTEXT_MSG_2_008")
    msg2_count = capture2.count_message("UNIQUE_SEQUENTIAL_CONTEXT_MSG_2_008")

    with (
        isolated_logging.capture_streams() as capture3,
        amod_logging.useRootLevel("DEBUG"),
    ):
        logger.debug("UNIQUE_SEQUENTIAL_CONTEXT_MSG_3_008")
    msg3_count = capture3.count_message("UNIQUE_SEQUENTIAL_CONTEXT_MSG_3_008")

    # Each should appear exactly once (not 14-17 times like the bug)
    for i, count in enumerate([msg1_count, msg2_count, msg3_count], 1):
        assert count == 1, (
            f"Sequential context message {i} appeared {count} times "
            "(expected 1). "
            "This indicates the sequential useRootLevel bug."
        )
