# Testing Guide: Pytest Helpers for Isolated Logging

This guide explains how to use the apathetic-logging pytest helpers to properly isolate logging in your test suite. If your project uses apathetic-logging and struggles with log level settings leaking between tests or wants automatic verbose debugging, this guide is for you.

## Table of Contents

1. [Introduction](#introduction)
2. [Quick Start](#quick-start)
3. [Installation](#installation)
4. [Scenario A: Debugging with TEST Level](#scenario-a-debugging-with-test-level)
5. [Scenario B: Testing Log Level Changes](#scenario-b-testing-log-level-changes)
6. [Scenario C: Complete Test Isolation](#scenario-c-complete-test-isolation)
7. [Root Logger vs App Logger Patterns](#root-logger-vs-app-logger-patterns)
8. [Advanced Usage](#advanced-usage)
9. [API Reference](#api-reference)
10. [Best Practices](#best-practices)
11. [Common Pitfalls](#common-pitfalls)
12. [Complete Working Examples](#complete-working-examples)

## Introduction

When testing applications that use apathetic-logging, you may encounter problems with:

1. **Limited debugging information**: Tests fail but you don't have enough log output to understand why
2. **Log level leakage**: One test sets the log level, and it affects subsequent tests
3. **Configuration conflicts**: Your tests want one log level, but your app wants a different one

The pytest helpers in this guide solve these problems by providing fixtures that:

- **Automatically reset logging state** between tests, preventing leakage
- **Provide TEST level debugging** that shows all logs even when tests fail
- **Allow you to test log level changes** (e.g., CLI arguments)
- **Give you fine-grained control** over logging during tests

## Quick Start

If you just want to get started quickly:

### For Debugging (See All Logs When Tests Fail)

```python
from apathetic_testing.pytest_helpers import LoggingTestLevel

def test_my_feature(loggingTestLevel: LoggingTestLevel) -> None:
    # Root logger is set to TEST level (most verbose)
    my_app.run()
    # All logs visible for debugging
```

### For Testing Log Level Changes

```python
from apathetic_testing.pytest_helpers import LoggingLevelTesting
import pytest

@pytest.mark.initial_level("ERROR")
def test_cli_debug_flag(loggingLevelTesting: LoggingLevelTesting) -> None:
    cli.main(["--log-level", "debug"])
    loggingLevelTesting.assertLevelChangedFrom("ERROR", to="DEBUG")
```

### For Complete Isolation

```python
from apathetic_testing.pytest_helpers import LoggingIsolation
import logging

def test_first(isolatedLogging: LoggingIsolation) -> None:
    isolatedLogging.setRootLevel("DEBUG")

def test_second(isolatedLogging: LoggingIsolation) -> None:
    # First test's state is not here
    assert isolatedLogging.getRootLogger().level != logging.DEBUG
```

## Installation

### Option 1: Direct Import in Tests

Simply import the fixtures directly in your test files:

```python
from apathetic_testing.pytest_helpers import (
    isolatedLogging,
    loggingTestLevel,
    loggingLevelTesting,
    apatheticLogger,
)
```

### Option 2: Add to conftest.py

For project-wide access, add to your `tests/conftest.py`:

```python
# tests/conftest.py
from apathetic_testing.pytest_helpers import (
    isolatedLogging,
    loggingTestLevel,
    loggingLevelTesting,
    apatheticLogger,
)

# Re-export for test discovery
__all__ = [
    "isolatedLogging",
    "loggingTestLevel",
    "loggingLevelTesting",
    "apatheticLogger",
]
```

Then use in any test:

```python
# tests/test_my_app.py
from apathetic_testing.pytest_helpers import LoggingTestLevel

def test_feature(loggingTestLevel: LoggingTestLevel) -> None:
    my_app.run()
```

## Scenario A: Debugging with TEST Level

### When to Use

Use `loggingTestLevel` when:

- You want maximum verbosity (all DEBUG and TRACE logs) when tests fail
- Your app has a default log level that's not verbose enough for debugging
- You want TEST/TRACE logs to bypass pytest's output capture to stderr

### How It Works

The `loggingTestLevel` fixture:

1. Sets the root logger to TEST level (most verbose: value 2)
2. **Prevents downgrades** - your app can't set a less verbose level
3. Allows **upgrades** - your app can switch to TRACE for even more detail
4. Provides a context manager to **temporarily allow level changes** when needed

### Basic Example

```python
from apathetic_testing.pytest_helpers import LoggingTestLevel

def test_app_with_verbose_logs(loggingTestLevel: LoggingTestLevel) -> None:
    # Root logger is at TEST level - all logs visible
    my_app.initialize()
    my_app.process_data()
    # All DEBUG/TRACE logs visible for debugging
```

### With Temporary Override

Sometimes your app needs to set its own level for specific configurations. Use the context manager:

```python
from apathetic_testing.pytest_helpers import LoggingTestLevel

def test_app_with_temp_override(loggingTestLevel: LoggingTestLevel) -> None:
    # Normal behavior: prevents downgrades
    app.configure_logging(level="INFO")  # Ignored, stays at TEST

    # But you can temporarily allow it
    with loggingTestLevel.temporarilyAllowChanges():
        app.configure_logging(level="WARNING")  # Now changes to WARNING

    # Prevention re-enabled after the context
    app.configure_logging(level="ERROR")  # Ignored, stays at WARNING
```

### Understanding TEST Level

The TEST level is 2 (DEBUG - 8) and has special behavior:

- **More verbose than DEBUG**: Shows TRACE, DEBUG, and all other levels
- **Bypasses pytest's capsys**: Logs to `sys.__stderr__` instead of `sys.stderr`
  - This means logs appear even when pytest captures output
  - Useful for debugging test failures without breaking output assertions

```python
# This is visible even with pytest's capsys
root_logger.test("This message bypasses capsys")
root_logger.trace("So does this")
root_logger.debug("And this")
```

## Scenario B: Testing Log Level Changes

### When to Use

Use `loggingLevelTesting` when:

- Your app has a `--log-level` CLI argument
- You're testing different logging configurations
- You want to verify your app actually changes the log level when configured
- You need to test both verbose and quiet logging modes

### How It Works

The `loggingLevelTesting` fixture:

1. Sets an **initial baseline level** (default: ERROR for quiet)
2. **Tracks all level changes** during the test
3. Provides **assertions** to verify changes happened
4. Provides **history** of all changes for inspection

### Basic Example

```python
from apathetic_testing.pytest_helpers import LoggingLevelTesting
import pytest

@pytest.mark.initial_level("ERROR")  # Start quiet
def test_cli_debug_flag(loggingLevelTesting: LoggingLevelTesting) -> None:
    # Verify we start at ERROR
    loggingLevelTesting.assertRootLevel("ERROR")

    # Run CLI with debug flag
    cli.main(["--log-level", "debug"])

    # Verify it changed to DEBUG
    loggingLevelTesting.assertRootLevel("DEBUG")

    # Verify the transition happened
    loggingLevelTesting.assertLevelChangedFrom("ERROR", to="DEBUG")
```

### Parametrized Testing

Test all log levels in one test:

```python
from apathetic_testing.pytest_helpers import LoggingLevelTesting
import pytest

@pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING", "ERROR"])
def test_all_log_levels(loggingLevelTesting: LoggingLevelTesting, level: str) -> None:
    cli.main(["--log-level", level.lower()])
    loggingLevelTesting.assertRootLevel(level)
```

### Testing Quiet Modes

Test that your app can be made quiet:

```python
from apathetic_testing.pytest_helpers import LoggingLevelTesting
import logging
import pytest

@pytest.mark.initial_level("DEBUG")  # Start verbose
def test_quiet_flag(loggingLevelTesting: LoggingLevelTesting) -> None:
    cli.main(["--quiet"])

    # Verify it made it quieter
    assert loggingLevelTesting.getRootLogger().level > logging.DEBUG
```

### Custom Initial Levels

Use any initial level:

```python
from apathetic_testing.pytest_helpers import LoggingLevelTesting
import pytest

@pytest.mark.initial_level("INFO")
def test_with_info_baseline(loggingLevelTesting: LoggingLevelTesting) -> None:
    loggingLevelTesting.assertRootLevel("INFO")
    # ... rest of test
```

### Inspecting Level History

Get the full history of changes:

```python
from apathetic_testing.pytest_helpers import LoggingLevelTesting

def test_inspect_history(loggingLevelTesting: LoggingLevelTesting) -> None:
    cli.main(["--log-level", "debug"])
    cli.main(["--log-level", "error"])

    history = loggingLevelTesting.getLevelHistory()

    # history is: [(timestamp, level_int, level_name), ...]
    level_names = [h[2] for h in history]
    assert "ERROR" in level_names  # Initial
    assert "DEBUG" in level_names
    assert "ERROR" in level_names  # Final
```

## Scenario C: Complete Test Isolation

### When to Use

Use `isolatedLogging` when:

- You want guaranteed isolation - no state leakage between tests
- You're building a library with its own logging configuration
- You want explicit control over logger creation and cleanup
- You're using parametrized tests with different logging configurations

### How It Works

The `isolatedLogging` fixture:

1. **Saves** complete logging state before test
2. **Clears** all loggers and resets to defaults
3. **Yields** a helper object for test use
4. **Restores** the saved state after test

Everything saved/restored:
- Logger class
- Registry data (8 configuration fields)
- All loggers in the registry
- Root logger state (level, handlers, propagate, disabled, filters)
- User configuration flags

### Basic Example

```python
from apathetic_testing.pytest_helpers import LoggingIsolation
import logging

def test_logger_isolation(isolatedLogging: LoggingIsolation) -> None:
    # Create and configure loggers
    logger = isolatedLogging.getLogger("myapp")
    logger.setLevel("DEBUG")

    assert logger.level == logging.DEBUG

def test_no_state_bleeding(isolatedLogging: LoggingIsolation) -> None:
    # Previous test's logger configuration is gone
    logger = isolatedLogging.getLogger("myapp")
    assert logger.level == logging.NOTSET  # Fresh state
```

### Working with Root Logger

```python
from apathetic_testing.pytest_helpers import LoggingIsolation

def test_root_logger(isolatedLogging: LoggingIsolation) -> None:
    # Get root logger
    root = isolatedLogging.getRootLogger()

    # Set its level
    isolatedLogging.setRootLevel("WARNING")

    # Verify with assertion
    isolatedLogging.assertRootLevel("WARNING")
```

### Working with Multiple Loggers

```python
from apathetic_testing.pytest_helpers import LoggingIsolation

def test_multiple_loggers(isolatedLogging: LoggingIsolation) -> None:
    app_logger = isolatedLogging.getLogger("myapp")
    lib_logger = isolatedLogging.getLogger("mylib")

    app_logger.setLevel("DEBUG")
    lib_logger.setLevel("WARNING")

    # Get all loggers
    all_loggers = isolatedLogging.getAllLoggers()
    assert "myapp" in all_loggers
    assert "mylib" in all_loggers
```

### With Parametrized Tests

Each parameter run gets fresh state:

```python
from apathetic_testing.pytest_helpers import LoggingIsolation
import logging
import pytest

@pytest.mark.parametrize("log_level", ["DEBUG", "INFO", "WARNING"])
def test_isolation_per_param(isolatedLogging: LoggingIsolation, log_level: str) -> None:
    isolatedLogging.setRootLevel(log_level)

    # Each run has its own isolated state
    assert isolatedLogging.getRootLogger().level == logging.getLevelName(log_level)
```

## Root Logger vs App Logger Patterns

Apathetic-logging supports two patterns. Understanding which your app uses helps choose the right fixture.

### Pattern 1: Root Logger (CLI Apps, Centralized Control)

Your app uses the root logger as the **single source of truth**:

```python
# Your app code
import apathetic_logging

apathetic_logging.setRootLevel("INFO")
app_logger = apathetic_logging.getLogger("myapp")  # level=NOTSET, inherits from root
lib_logger = apathetic_logging.getLogger("mylib")  # level=NOTSET, inherits from root

app_logger.debug("...")  # Uses root's level
lib_logger.debug("...")  # Uses root's level
```

**Best fixture**: `loggingTestLevel` or `loggingLevelTesting`

**In tests**:
```python
from apathetic_testing.pytest_helpers import LoggingIsolation
import logging

def test_root_pattern(isolatedLogging: LoggingIsolation) -> None:
    # Set root level - all children inherit
    isolatedLogging.setRootLevel("INFO")

    # Children inherit effective level
    logger = isolatedLogging.getLogger("myapp")
    assert logger.getEffectiveLevel() == logging.INFO
```

### Pattern 2: App Logger (Libraries, Independent Control)

Your app creates its own named logger and controls it independently:

```python
# Your app code
import apathetic_logging

lib_logger = apathetic_logging.getLogger("mylib")
lib_logger.setLevel("WARNING")
lib_logger.propagate = False  # Don't inherit from root

lib_logger.debug("...")  # Won't be visible (WARNING level)
```

**Best fixture**: `isolatedLogging`

**In tests**:
```python
from apathetic_testing.pytest_helpers import LoggingIsolation
import logging

def test_app_pattern(isolatedLogging: LoggingIsolation) -> None:
    # Create isolated logger
    logger = isolatedLogging.getLogger("mylib")
    logger.setLevel("DEBUG")
    logger.propagate = False

    # This logger controls its own logging
    assert logger.level == logging.DEBUG
```

### Hybrid Approach

Some apps use both patterns. Just be aware of how your app is structured:

```python
# App code
apathetic_logging.setRootLevel("INFO")  # Root pattern
log = apathetic_logging.getLogger("myapp")  # Inherits from root

# But also
lib_logger = apathetic_logging.getLogger("mylib")
lib_logger.setLevel("DEBUG")
lib_logger.propagate = False  # Library pattern

# In tests
from apathetic_testing.pytest_helpers import LoggingIsolation

def test_hybrid(isolatedLogging: LoggingIsolation) -> None:
    # Test root-based loggers
    isolatedLogging.setRootLevel("WARNING")
    # ... test ...

    # Test independent loggers
    lib = isolatedLogging.getLogger("mylib")
    lib.setLevel("DEBUG")
    # ... test ...
```

## Advanced Usage

### Combining Multiple Fixtures

You can use multiple fixtures in one test:

```python
from apathetic_testing.pytest_helpers import LoggingTestLevel, LoggingIsolation
from logging import Logger

def test_complex_scenario(
    loggingTestLevel: LoggingTestLevel,
    apatheticLogger: Logger,
    isolatedLogging: LoggingIsolation,
) -> None:
    # All three fixtures available
    # loggingTestLevel: Prevents downgrades from TEST
    # apatheticLogger: Fresh test logger with unique name
    # isolatedLogging: Full state control and isolation

    root = isolatedLogging.getRootLogger()
    apatheticLogger.debug("message")
    loggingTestLevel.allowAppLevelChange()
```

### Class-Based Tests

All fixtures work with pytest's class-based tests:

```python
from apathetic_testing.pytest_helpers import LoggingIsolation

class TestAppLogging:
    def test_one(self, isolatedLogging: LoggingIsolation) -> None:
        isolatedLogging.setRootLevel("DEBUG")

    def test_two(self, isolatedLogging: LoggingIsolation) -> None:
        # Fresh state for each test
        root = isolatedLogging.getRootLogger()
```

### Custom Assertions

Use the assertion helper functions:

```python
from apathetic_testing.pytest_helpers import (
    LoggingIsolation,
    assertLevelEquals,
    assertRootLevelEquals,
    assertHandlerCount,
)

def test_with_custom_assertions(isolatedLogging: LoggingIsolation) -> None:
    logger = isolatedLogging.getLogger("myapp")
    logger.setLevel("DEBUG")

    # Various assertion styles
    assertLevelEquals(logger, "DEBUG", effective=False)
    assertHandlerCount(logger, 0)  # No handlers (inherits from root)

    root = isolatedLogging.getRootLogger()
    assertRootLevelEquals("DEBUG")
```

### Manual State Save/Restore

For advanced use cases:

```python
from apathetic_testing.pytest_helpers import saveLoggingState, restoreLoggingState, LoggingState
import logging

def test_manual_state_management() -> None:
    # Save state
    saved: LoggingState = saveLoggingState()

    # Modify logging
    logging.setLoggerClass(MyCustomLogger)
    import apathetic_logging
    apathetic_logging.setRootLevel("DEBUG")

    # ... test ...

    # Restore if needed
    restoreLoggingState(saved)
```

## API Reference

### Fixtures

#### `isolatedLogging`

**Type**: `Generator[LoggingIsolation, None, None]`

**Provides**: `LoggingIsolation` - Helper for complete logging isolation

**Methods**:
- `getRootLogger() -> Logger` - Get the root logger
- `getLogger(name: str | None = None) -> Logger` - Get a logger by name
- `setRootLevel(level: str | int) -> None` - Set root logger level
- `getAllLoggers() -> dict[str, Logger]` - Get all loggers
- `assertRootLevel(expected: str | int) -> None` - Assert root level
- `assertLoggerLevel(name: str, expected: str | int) -> None` - Assert logger level
- `captureStreams() -> StreamCapture` - Context manager for capturing log messages

**Example with message capture**:
```python
def test_message_count(isolatedLogging: LoggingIsolation) -> None:
    logger = isolatedLogging.getLogger("myapp")
    logger.setLevel(logging.DEBUG)

    with isolatedLogging.captureStreams() as capture:
        logger.debug("test message")

    # Count exact message occurrences
    count = capture.countMessage("test message")
    assert count == 1
```

#### `loggingTestLevel`

**Type**: `Generator[LoggingTestLevel, None, None]`

**Provides**: `LoggingTestLevel` - Helper for TEST level debugging

**Methods**:
- `allowAppLevelChange() -> None` - Allow level downgrades
- `preventAppLevelChange() -> None` - Prevent level downgrades (default)
- `getCurrentLevel() -> int` - Get current root logger level
- `temporarilyAllowChanges() -> contextmanager` - Context manager for temporary changes

#### `loggingLevelTesting`

**Type**: `Generator[LoggingLevelTesting, None, None]`

**Provides**: `LoggingLevelTesting` - Helper for testing level changes

**Methods**:
- `assertRootLevel(expected: str | int) -> None` - Assert current level
- `assertLevelChangedFrom(old: str | int, *, to: str | int) -> None` - Assert transition
- `assertLevelNotChanged() -> None` - Assert level never changed
- `getLevelHistory() -> list[tuple[float, int, str]]` - Get change history
- `resetToInitial() -> None` - Reset to initial level

**Marks**:
- `@pytest.mark.initial_level(level: str)` - Set initial level (default: "ERROR")

#### `apatheticLogger`

**Type**: `Logger`

**Provides**: A fresh logger with unique name and TEST level

**Example**:
```python
from logging import Logger

def test_logger_methods(apatheticLogger: Logger) -> None:
    apatheticLogger.debug("message")
```

### Utility Classes and Functions

#### `StreamCapture` (Context Manager)

**Purpose**: Capture log records to count message occurrences. Works reliably in xdist parallel mode and stitched mode.

**Type**: Context manager (use with `with` statement)

**Methods**:
- `countMessage(message: str) -> int` - Count exact message occurrences

**When to use**:
- Detecting message duplication
- Verifying exact message text appears correct number of times
- Testing in parallel mode (xdist) or stitched mode (where caplog fails)

**Example**:
```python
from apathetic_testing.pytest_helpers import LoggingIsolation
import logging

def test_no_duplication(isolatedLogging: LoggingIsolation) -> None:
    logger = isolatedLogging.getLogger("myapp")
    logger.setLevel(logging.DEBUG)

    # Capture messages as they're logged
    with isolatedLogging.captureStreams() as capture:
        logger.debug("unique message")

    # Count exact occurrences (should be 1, not 2)
    count = capture.countMessage("unique message")
    assert count == 1
```

#### Utility Functions

```python
def saveLoggingState() -> LoggingState:
    """Save complete logging state."""

def restoreLoggingState(state: LoggingState) -> None:
    """Restore logging state from snapshot."""

def clearAllLoggers() -> None:
    """Remove all loggers except root."""

def assertLevelEquals(
    logger: logging.Logger,
    expected: str | int,
    *,
    effective: bool = True,
) -> None:
    """Assert logger has expected level."""

def assertRootLevelEquals(expected: str | int) -> None:
    """Assert root logger has expected level."""

def assertHandlerCount(
    logger: logging.Logger,
    expected: int,
    *,
    handler_type: type[logging.Handler] | None = None,
) -> None:
    """Assert logger has expected handler count."""
```

## Best Practices

### 1. One Fixture Per Test

Use the simplest fixture that meets your needs:

```python
from apathetic_testing.pytest_helpers import LoggingIsolation, LoggingLevelTesting, LoggingTestLevel

# Good: Just need isolation
def test_isolation(isolatedLogging: LoggingIsolation) -> None:
    pass

# Good: Testing level changes
def test_changes(loggingLevelTesting: LoggingLevelTesting) -> None:
    pass

# Good: Need TEST level
def test_debugging(loggingTestLevel: LoggingTestLevel) -> None:
    pass
```

### 2. Use Meaningful Initial Levels

When testing level changes, choose initial levels that make sense:

```python
from apathetic_testing.pytest_helpers import LoggingLevelTesting
import pytest

# Good: Start with ERROR (quiet) to test that app makes it verbose
@pytest.mark.initial_level("ERROR")
def test_debug_flag(loggingLevelTesting: LoggingLevelTesting) -> None:
    cli.main(["--debug"])

# Good: Start with DEBUG (verbose) to test that app makes it quiet
@pytest.mark.initial_level("DEBUG")
def test_quiet_flag(loggingLevelTesting: LoggingLevelTesting) -> None:
    cli.main(["--quiet"])
```

### 3. Prefer Context Managers for Temporary Changes

Instead of manual on/off:

```python
from apathetic_testing.pytest_helpers import LoggingTestLevel

# Good: Clear intent, automatic cleanup
def test_example(loggingTestLevel: LoggingTestLevel) -> None:
    with loggingTestLevel.temporarilyAllowChanges():
        app.configure(level="WARNING")

    # Less clear and error-prone
    loggingTestLevel.allowAppLevelChange()
    app.configure(level="WARNING")
    loggingTestLevel.preventAppLevelChange()
```

### 4. Check History for Complex Scenarios

When testing complex level change sequences:

```python
from apathetic_testing.pytest_helpers import LoggingLevelTesting

def test_complex_config(loggingLevelTesting: LoggingLevelTesting) -> None:
    cli.main(args_that_change_level_multiple_times())

    history = loggingLevelTesting.getLevelHistory()
    levels = [h[2] for h in history]

    assert levels == ["ERROR", "INFO", "DEBUG"]  # Expected sequence
```

### 5. Don't Mix Paradigms

Stick to one pattern per test:

```python
from apathetic_testing.pytest_helpers import LoggingIsolation

# Good: Testing root pattern only
def test_root_only(isolatedLogging: LoggingIsolation) -> None:
    isolatedLogging.setRootLevel("INFO")
    # Test root-based logging

# Good: Testing app pattern only
def test_app_only(isolatedLogging: LoggingIsolation) -> None:
    logger = isolatedLogging.getLogger("myapp")
    logger.setLevel("DEBUG")
    # Test app-based logging

# Less ideal: Mixing both in same test (confusing)
def test_mixed(isolatedLogging: LoggingIsolation) -> None:
    isolatedLogging.setRootLevel("INFO")  # Root pattern
    logger = isolatedLogging.getLogger("myapp")
    logger.setLevel("DEBUG")  # App pattern
    # Which controls what?
```

### 6. Use StreamCapture for Message Counting and Duplication Tests

When you need to count exact message occurrences or test for duplication, use `StreamCapture` instead of pytest's `caplog`:

```python
from apathetic_testing.pytest_helpers import LoggingIsolation
import logging

# Good: Works in all modes (serial, parallel, stitched)
def test_no_duplication(isolatedLogging: LoggingIsolation) -> None:
    logger = isolatedLogging.getLogger("myapp")
    logger.setLevel(logging.DEBUG)

    with isolatedLogging.captureStreams() as capture:
        logger.debug("message")

    # Count exact occurrences
    count = capture.countMessage("message")
    assert count == 1  # Not 2 or more

# Less ideal: caplog may fail in parallel/stitched modes
def test_with_caplog(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.DEBUG):
        logger.debug("message")

    # This count might be 0 or wrong in xdist workers or stitched mode
    count = sum(1 for r in caplog.records if r.getMessage() == "message")
    assert count == 1
```

**Why this matters**: `StreamCapture` captures log records at the logging level, independent of pytest's infrastructure. This makes it:
- **Parallel-safe**: Works correctly in xdist worker processes
- **Stitched-safe**: Works in single-file stitched distribution
- **Consistent**: Same behavior across all runtime modes
- **Simple**: Just call `countMessage()`

**When to use each**:
- Use `StreamCapture.countMessage()` for: Counting message occurrences, detecting duplication
- Use `caplog.records` for: Filtering by level, checking logger names, accessing log metadata

## Common Pitfalls

### Pitfall 1: Forgetting Isolation Needs Setup

Test framework expectations vary. Be explicit:

```python
from apathetic_testing.pytest_helpers import LoggingLevelTesting, LoggingIsolation
import pytest

# Good: Explicit about what we're testing
@pytest.mark.initial_level("ERROR")
def test_something(loggingLevelTesting: LoggingLevelTesting) -> None:
    # Explicitly starts at ERROR

# Less clear: What's the baseline?
def test_something_unclear(isolatedLogging: LoggingIsolation) -> None:
    isolatedLogging.setRootLevel("ERROR")  # What was it before?
```

### Pitfall 2: Assuming Logger Inheritance Works Automatically

Child loggers don't automatically inherit from root until you set propagate correctly:

```python
from apathetic_testing.pytest_helpers import LoggingIsolation
import logging

# Good: Clear propagation
def test_propagation(isolatedLogging: LoggingIsolation) -> None:
    isolatedLogging.setRootLevel("INFO")

    child = isolatedLogging.getLogger("myapp.module")
    # child.level is NOTSET (default), so inherits from root
    assert child.getEffectiveLevel() == logging.INFO

# Pitfall: Manual level setting prevents inheritance
def test_wrong_inheritance(isolatedLogging: LoggingIsolation) -> None:
    isolatedLogging.setRootLevel("INFO")

    child = isolatedLogging.getLogger("myapp.module")
    child.setLevel("DEBUG")  # Now explicitly DEBUG, doesn't inherit
    assert child.getEffectiveLevel() == logging.DEBUG  # Not INFO
```

### Pitfall 3: Modifying Fixtures in Other Modules

Don't import and modify fixture behavior from other modules:

```python
# Bad: Modifying imported fixture in test module
import apathetic_logging
from apathetic_testing.pytest_helpers import LoggingIsolation

def test_something(isolatedLogging: LoggingIsolation) -> None:
    # This might not work as expected if isolatedLogging's
    # monkeypatch isn't in this namespace
    apathetic_logging.setRootLevel("DEBUG")
```

Instead, use the fixture's helper:

```python
# Good: Using fixture helper
from apathetic_testing.pytest_helpers import LoggingIsolation

def test_something(isolatedLogging: LoggingIsolation) -> None:
    isolatedLogging.setRootLevel("DEBUG")
```

### Pitfall 4: Not Resetting in Class-Based Tests

pytest fixtures work with class-based tests, but reset between methods:

```python
from apathetic_testing.pytest_helpers import LoggingIsolation
import logging

# Good: Understands fixture resets between methods
class TestLogging:
    def test_first(self, isolatedLogging: LoggingIsolation) -> None:
        isolatedLogging.setRootLevel("DEBUG")

    def test_second(self, isolatedLogging: LoggingIsolation) -> None:
        # Fresh fixture - level is reset
        root = isolatedLogging.getRootLogger()
        assert root.level != logging.DEBUG
```

### Pitfall 5: Confusing TEST_LEVEL and TEST Name

TEST_LEVEL (integer 2) is different from test level detection:

```python
from apathetic_testing.pytest_helpers import LoggingIsolation
import apathetic_logging

# These are different
apathetic_logging.TEST_LEVEL  # The integer level (2)
"TEST"  # The string level name

# Good: Know the difference
def test_example(isolatedLogging: LoggingIsolation) -> None:
    root = isolatedLogging.getRootLogger()
    root.setLevel(apathetic_logging.TEST_LEVEL)  # Integer
    apathetic_logging.setRootLevel("TEST")  # String
    assert root.level == apathetic_logging.TEST_LEVEL  # Both work
```

### Pitfall 6: Using pytest's caplog for Message Counting

**Problem**: pytest's `caplog` fixture doesn't work reliably for counting log message occurrences in:
- **xdist parallel mode**: caplog captures records inconsistently in worker processes
- **stitched mode**: Handler identity checks (`isinstance()`) fail, causing double-capture
- **When handlers are dynamically added**: apathetic-logging's `manageHandlers()` may add handlers after caplog setup

```python
# Bad: caplog fails in parallel/stitched modes
def test_no_duplication(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.DEBUG):
        logger.debug("message")

    # In xdist workers or stitched mode, count may be 0 or incorrect
    count = sum(1 for r in caplog.records if r.getMessage() == "message")
    assert count == 1  # May fail in parallel/stitched modes
```

**Solution**: Use `StreamCapture` (built-in to `LoggingIsolation`) instead:

```python
# Good: Works in all modes (parallel, stitched, serial)
def test_no_duplication(isolatedLogging: LoggingIsolation) -> None:
    with isolatedLogging.captureStreams() as capture:
        logger.debug("message")

    count = capture.countMessage("message")
    assert count == 1  # Works reliably in all modes
```

**Why this works**: `StreamCapture` captures log records directly at the logging level, not through pytest's handler infrastructure. This works with apathetic-logging's handler system and doesn't depend on pytest's worker process behavior.

**When to use each approach**:
- Use `caplog` for: Asserting log levels, checking logger names, filtering by level
- Use `captureStreams()` for: Counting message occurrences, detecting duplication, checking exact message text

**Example: Detecting Message Duplication**

```python
import logging
import pytest
from apathetic_testing.pytest_helpers import LoggingIsolation

def test_child_logger_no_duplication(isolatedLogging: LoggingIsolation) -> None:
    """Verify messages from child loggers don't appear multiple times."""
    root = isolatedLogging.getRootLogger()
    child = isolatedLogging.getLogger("my.child")

    root.setLevel(logging.DEBUG)
    child.setLevel(logging.DEBUG)
    child.propagate = True

    # Capture messages as they're logged
    with isolatedLogging.captureStreams() as capture:
        child.debug("unique message")

    # Count exact message occurrences
    count = capture.countMessage("unique message")

    # Should be 1, not 2 or more (duplication bug)
    assert count == 1, f"Expected message once, got {count} times"
```

## Complete Working Examples

### Example 1: CLI App with --log-level Argument

```python
# tests/test_cli.py
import pytest
from myapp.cli import main
from apathetic_testing.pytest_helpers import LoggingLevelTesting

@pytest.mark.initial_level("WARNING")
def test_verbose_flag(loggingLevelTesting: LoggingLevelTesting) -> None:
    """Test that --verbose flag sets DEBUG level."""
    main(["--verbose", "command"])
    loggingLevelTesting.assertLevelChangedFrom("WARNING", to="DEBUG")

@pytest.mark.initial_level("INFO")
def test_quiet_flag(loggingLevelTesting: LoggingLevelTesting) -> None:
    """Test that --quiet flag sets ERROR level."""
    main(["--quiet", "command"])
    loggingLevelTesting.assertLevelChangedFrom("INFO", to="ERROR")

@pytest.mark.parametrize("flag,expected_level", [
    ("--trace", "TRACE"),
    ("--verbose", "DEBUG"),
    ("--normal", "INFO"),
    ("--quiet", "WARNING"),
    ("--silent", "SILENT"),
])
def test_all_log_level_flags(loggingLevelTesting: LoggingLevelTesting, flag: str, expected_level: str) -> None:
    """Test all log level flags."""
    main([flag, "command"])
    loggingLevelTesting.assertRootLevel(expected_level)
```

### Example 2: Library with Own Logging Configuration

```python
# tests/test_mylib.py
from mylib import MyLibrary
from apathetic_testing.pytest_helpers import LoggingIsolation
import logging
import pytest

def test_library_logging_isolation(isolatedLogging: LoggingIsolation) -> None:
    """Test that library sets its own logging independently."""
    lib = MyLibrary(log_level="DEBUG")

    # Verify library's logger level
    lib_logger = isolatedLogging.getLogger("mylib")
    assert lib_logger.getEffectiveLevel() == logging.DEBUG

def test_library_doesnt_affect_root(isolatedLogging: LoggingIsolation) -> None:
    """Test that library doesn't change root logger."""
    # Set root to WARNING
    isolatedLogging.setRootLevel(logging.WARNING)

    # Library sets its own level
    lib = MyLibrary(log_level="DEBUG")

    # Root should be unchanged
    isolatedLogging.assertRootLevel(logging.WARNING)

@pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING", "ERROR"])
def test_library_respects_all_levels(isolatedLogging: LoggingIsolation, level: str) -> None:
    """Test library works with all log levels."""
    lib = MyLibrary(log_level=level)
    lib.process()  # Should work regardless of level
```

### Example 3: Complex Application Setup

```python
# tests/test_complex_app.py
import pytest
from myapp import App
from apathetic_testing.pytest_helpers import (
    LoggingTestLevel,
    LoggingIsolation,
    LoggingLevelTesting,
)
from logging import Logger
import apathetic_logging

def test_app_initialization_with_debugging(loggingTestLevel: LoggingTestLevel) -> None:
    """Test app initialization with maximum verbosity."""
    # Root is at TEST level
    app = App()

    # App tries to set INFO (ignored)
    app.configure_logging("INFO")

    # All logs visible
    current_level = loggingTestLevel.getCurrentLevel()
    assert current_level == apathetic_logging.TEST_LEVEL

def test_app_with_custom_logger(isolatedLogging: LoggingIsolation, apatheticLogger: Logger) -> None:
    """Test app with custom test logger."""
    app = App()
    app.set_logger(apatheticLogger)

    # Run with test logger
    app.run()

    # Verify test logger was used
    assert apatheticLogger.levelname == "TEST"

@pytest.mark.initial_level("ERROR")
def test_app_configuration_changes(loggingLevelTesting: LoggingLevelTesting) -> None:
    """Test that app can configure logging properly."""
    app = App()

    # Start at ERROR
    assert app.get_log_level() == "ERROR"

    # Configure to DEBUG
    app.configure_logging("DEBUG")
    loggingLevelTesting.assertLevelChangedFrom("ERROR", to="DEBUG")

    # Back to ERROR
    app.configure_logging("ERROR")
    loggingLevelTesting.assertRootLevel("ERROR")

class TestAppIntegration:
    """Integration tests with isolation."""

    def test_first_scenario(self, isolatedLogging: LoggingIsolation) -> None:
        app = App(log_level="DEBUG")
        app.run()

    def test_second_scenario(self, isolatedLogging: LoggingIsolation) -> None:
        # Fresh state - not affected by first test
        app = App(log_level="WARNING")
        app.run()
```

---

## Questions?

For more information, see:

- [Apathetic Logging API Documentation](./api.md)
- [Github Issues](https://github.com/apathetic-tools/apathetic-python-logging/issues)
- [Project Repository](https://github.com/apathetic-tools/apathetic-python-logging)
