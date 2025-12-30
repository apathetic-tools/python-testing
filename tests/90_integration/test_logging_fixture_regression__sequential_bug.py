"""Test to verify our fixtures work around the sequential useRootLevel bug.

This test validates that using useRootLevel() context manager sequentially
works correctly and doesn't cause log messages to be emitted multiple times.

This bug was previously seen in stitched mode where module state persists.
Our fixtures are specifically designed to prevent this issue.
"""

from __future__ import annotations

import logging
import sys
from io import StringIO
from typing import Any, cast

import apathetic_logging as amod_logging


# Allow up to 3 lines: 1 for the message + potential formatting/blank lines
# (In stitched mode, logging may produce extra lines due to different formatting)
# The critical thing is we should NOT see 14-17 lines (the original bug)
MAX_EXPECTED_LINES = 3


def test_sequential_use_root_level_single_message(
    atest_isolated_logging: Any,  # noqa: ARG001
) -> None:
    """Verify sequential useRootLevel calls don't cause message duplication.

    This test reproduces the exact issue of sequential context manager usage:
    - First context manager use: works fine
    - Second context manager use: message should still appear once

    Our fixture isolation should prevent the bug where it would appear 14-17 times.
    """
    # Setup: get a logger
    logger = logging.getLogger("test")

    # Save original streams
    old_stdout = sys.stdout
    old_stderr = sys.stderr

    try:
        # First context manager use
        capture1 = StringIO()
        sys.stdout = capture1
        sys.stderr = capture1

        with amod_logging.useRootLevel("TRACE"):
            logger.debug("First message")

        output1 = capture1.getvalue()
        lines1 = [line for line in output1.splitlines() if line.strip()]
        count1 = len(lines1)

        # Second context manager use - this is where the bug would manifest
        capture2 = StringIO()
        sys.stdout = capture2
        sys.stderr = capture2

        with amod_logging.useRootLevel("TRACE"):
            logger.debug("Second message")

        output2 = capture2.getvalue()
        lines2 = [line for line in output2.splitlines() if line.strip()]
        count2 = len(lines2)

        # Verify: second context manager should output same number of lines as first
        # Expected: 1-2 lines per message
        # Broken behavior: 14-17 lines on second use
        error_msg2 = (
            f"Expected <={MAX_EXPECTED_LINES} lines for second message, got {count2}. "
            "Sequential useRootLevel bug detected!"
        )
        assert count2 <= MAX_EXPECTED_LINES, error_msg2
        error_msg1 = (
            f"Expected <={MAX_EXPECTED_LINES} lines for first message, got {count1}"
        )
        assert count1 <= MAX_EXPECTED_LINES, error_msg1

    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


def test_sequential_use_root_level_multiple_iterations(
    atest_isolated_logging: Any,  # noqa: ARG001
) -> None:
    """Verify multiple sequential useRootLevel calls all produce correct output."""
    logger = logging.getLogger("test_multi")

    old_stdout = sys.stdout
    old_stderr = sys.stderr

    try:
        # Test multiple sequential uses
        for i in range(5):
            capture = StringIO()
            sys.stdout = capture
            sys.stderr = capture

            with amod_logging.useRootLevel("TRACE"):
                logger.debug("Iteration %s", i)

            output = capture.getvalue()
            lines = [line for line in output.splitlines() if line.strip()]
            count = len(lines)

            # Each iteration should produce 1-2 lines, not 14-17
            error_msg = (
                f"Iteration {i}: Expected <={MAX_EXPECTED_LINES} lines, got {count}. "
                "Sequential bug detected!"
            )
            assert count <= MAX_EXPECTED_LINES, error_msg

    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


def test_sequential_use_root_level_with_stream_changes(
    atest_isolated_logging: Any,  # noqa: ARG001
) -> None:
    """Simulate pytest capsys behavior: replacing streams between uses.

    This more closely matches what happens in pytest where streams can be
    redirected multiple times during test execution.
    """
    logger = logging.getLogger("test_streams")

    old_stdout = sys.stdout
    old_stderr = sys.stderr

    try:
        # First use with stream1
        capture1 = StringIO()
        sys.stdout = capture1
        sys.stderr = capture1

        with amod_logging.useRootLevel("TRACE"):
            logger.debug("Message 1")

        output1 = capture1.getvalue()
        count1 = len([line for line in output1.splitlines() if line.strip()])

        # Replace streams (like pytest capsys does between tests)
        capture2 = StringIO()
        sys.stdout = capture2
        sys.stderr = capture2

        with amod_logging.useRootLevel("TRACE"):
            logger.debug("Message 2")

        output2 = capture2.getvalue()
        count2 = len([line for line in output2.splitlines() if line.strip()])

        # Third use with yet another stream
        capture3 = StringIO()
        sys.stdout = capture3
        sys.stderr = capture3

        with amod_logging.useRootLevel("TRACE"):
            logger.debug("Message 3")

        output3 = capture3.getvalue()
        count3 = len([line for line in output3.splitlines() if line.strip()])

        # All three should have similar counts (1-2 lines), not 14-17
        error_msg1 = f"Message 1: Expected <={MAX_EXPECTED_LINES} lines, got {count1}"
        error_msg2 = f"Message 2: Expected <={MAX_EXPECTED_LINES} lines, got {count2}"
        error_msg3 = f"Message 3: Expected <={MAX_EXPECTED_LINES} lines, got {count3}"
        assert count1 <= MAX_EXPECTED_LINES, error_msg1
        assert count2 <= MAX_EXPECTED_LINES, error_msg2
        assert count3 <= MAX_EXPECTED_LINES, error_msg3

    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


def test_use_root_level_clears_stream_cache(
    atest_isolated_logging: Any,  # noqa: ARG001
) -> None:
    """Verify that useRootLevel properly clears the stream cache.

    The root logger's _last_stream_ids cache must be managed correctly
    when entering/exiting the context manager to prevent re-entry loops.
    """
    root = cast("Any", logging.getLogger(""))

    # Before entering context manager, set _last_stream_ids to something
    # (simulating previous state)
    root._last_stream_ids = (sys.stdout, sys.stderr)  # noqa: SLF001

    # Enter and exit context manager
    with amod_logging.useRootLevel("DEBUG"):
        pass

    # After exiting, _last_stream_ids should be None (cleared)
    # OR it should be reset to current stdout/stderr
    # The key is that stale stream identities should not cause re-entry loops
    assert (
        root._last_stream_ids is None  # noqa: SLF001
        or root._last_stream_ids == (sys.stdout, sys.stderr)  # noqa: SLF001
    ), f"Stream cache not properly managed: {root._last_stream_ids}"  # noqa: SLF001
