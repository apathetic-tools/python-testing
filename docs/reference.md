---
layout: base
title: API Reference
permalink: /reference/
---

# API Reference

Complete API documentation for Apathetic Python Testing.

## Quick Reference

| Category | Functions/Fixtures |
|----------|-----------|
| **Logging Fixtures** | [`isolated_logging`](#isolated_logging), [`logging_test_level`](#logging_test_level), [`logging_level_testing`](#logging_level_testing) |
| **Patching** | [`patch_everywhere()`](#patch_everywhere) |
| **Runtime Testing** | [`runtime_swap`](#runtime_swap), [`detect_module_runtime_mode()`](#detect_module_runtime_mode) |
| **System Detection** | [`is_running_under_pytest()`](#is_running_under_pytest) |
| **Mock Utilities** | [`create_mock_superclass_test()`](#create_mock_superclass_test) |
| **Build Utilities** | [`ensure_stitched_script_up_to_date()`](#ensure_stitched_script_up_to_date), [`ensure_zipapp_up_to_date()`](#ensure_zipapp_up_to_date) |

## Logging Fixtures

### isolated_logging

**Type:** Pytest fixture

**Import from:** `apathetic_testing.logging`

**Returns:** `LoggingIsolation` helper object

Provides complete test isolation for logging state. Saves the complete logging state before the test, clears all loggers and resets to defaults, then restores the saved state after the test.

**Methods:**
- `set_root_level(level: str | int) -> None` — Set root logger level
- `get_root_logger() -> logging.Logger` — Get the root logger
- `get_logger(name: str) -> logging.Logger` — Get a named logger
- `assert_root_level(expected: str | int) -> None` — Assert root logger level
- `get_all_loggers() -> dict[str, logging.Logger]` — Get all loggers
- `capture_streams() -> StreamCapture` — Context manager for capturing log messages

**Example:**
```python
from apathetic_testing.logging import isolated_logging

def test_logger_isolation(isolated_logging):
    # Each test gets fresh, isolated logging state
    isolated_logging.set_root_level("DEBUG")
    my_app.run()
    # State automatically reset after test
```

---

### logging_test_level

**Type:** Pytest fixture

**Import from:** `apathetic_testing.logging`

**Returns:** `LoggingTestLevel` helper object

Sets root logger to TEST level (most verbose) and prevents downgrades. Useful for debugging tests where you need to see all log output.

**Methods:**
- `allow_app_level_change() -> None` — Allow the app to change log levels
- `prevent_app_level_change() -> None` — Prevent the app from downgrading log levels (default)
- `get_current_level() -> int` — Get current root logger level
- `temporarily_allow_changes() -> contextmanager` — Context manager for temporary level changes

**Example:**
```python
from apathetic_testing.logging import logging_test_level

def test_with_verbose_logs(logging_test_level):
    # Root logger is at TEST level - maximum verbosity
    my_app.run()
    # All DEBUG and TRACE logs visible even if test fails
```

**Note:** The TEST level is 2 (more verbose than DEBUG) and bypasses pytest's capsys to write to `sys.__stderr__`, allowing logs to appear even when output is captured.

---

### logging_level_testing

**Type:** Pytest fixture (parametrizable with `@pytest.mark.initial_level`)

**Import from:** `apathetic_testing.logging`

**Returns:** `LoggingLevelTesting` helper object

Tracks all log level changes and provides assertions to verify them. Useful for testing CLI apps with `--log-level` arguments.

**Pytest Mark:**
```python
@pytest.mark.initial_level("ERROR")  # Set initial level (default: "ERROR")
def test_cli_debug_flag(logging_level_testing):
    cli.main(["--log-level", "debug"])
    logging_level_testing.assert_level_changed_from("ERROR", to="DEBUG")
```

**Methods:**
- `assert_root_level(expected: str | int) -> None` — Assert current level
- `assert_level_changed_from(old: str | int, *, to: str | int) -> None` — Assert a specific transition
- `assert_level_not_changed() -> None` — Assert level was never changed
- `get_level_history() -> list[tuple[float, int, str]]` — Get history of all changes (timestamp, level_int, level_name)
- `reset_to_initial() -> None` — Reset to initial level

**Example:**
```python
from apathetic_testing.logging import logging_level_testing
import pytest

@pytest.mark.initial_level("ERROR")
def test_verbose_flag(logging_level_testing):
    cli.main(["--verbose"])
    logging_level_testing.assert_level_changed_from("ERROR", to="DEBUG")
```

---

## Patching

### patch_everywhere

**Type:** Context manager

**Import from:** `apathetic_testing`

**Signature:**
```python
patch_everywhere(target: str, new) -> contextmanager
```

Safe patching that works reliably in package, stitched, and zipapp runtime modes. The standard `unittest.mock.patch` can fail in stitched or zipapp modes.

**Parameters:**
- `target` (str) — Target to patch (e.g., "module.function")
- `new` — Object to replace the target with (Mock, function, etc.)

**Example:**
```python
from apathetic_testing import patch_everywhere
from unittest.mock import Mock

def test_with_patching():
    # This patching works reliably in all runtime modes
    with patch_everywhere("module.function", Mock(return_value=42)):
        result = module.function()
        assert result == 42
```

**Why not use unittest.mock.patch?**
- Standard `patch()` uses module import inspection that fails in stitched/zipapp modes
- `patch_everywhere()` handles all runtime modes: package, stitched, and zipapp
- Guarantees consistent behavior across all distribution formats

---

## Runtime Testing

### runtime_swap

**Type:** Pytest fixture

**Import from:** `apathetic_testing`

Automatically swaps to stitched or zipapp mode for testing if available, falls back to package mode otherwise.

**Example:**
```python
from apathetic_testing import runtime_swap

def test_in_stitched_mode(runtime_swap):
    # Automatically runs against stitched build if available
    # Falls back to package mode if stitched not available
    import my_package
    result = my_package.function()
    assert result is not None
```

**Use Case:**
- Catch issues that only appear in stitched/zipapp distributions
- Test compatibility across all distribution formats

---

### detect_module_runtime_mode

**Type:** Function

**Import from:** `apathetic_testing`

**Signature:**
```python
detect_module_runtime_mode(module_name: str) -> str
```

Detect which runtime mode a module is executing in.

**Returns:** One of `"package"`, `"stitched"`, or `"zipapp"`

**Example:**
```python
from apathetic_testing import detect_module_runtime_mode

mode = detect_module_runtime_mode("my_package")
print(f"Running in {mode} mode")
```

---

## System Detection

### is_running_under_pytest

**Type:** Function

**Import from:** `apathetic_testing`

**Signature:**
```python
is_running_under_pytest() -> bool
```

Detect if code is running under pytest by checking environment variables and command-line arguments.

**Example:**
```python
from apathetic_testing import is_running_under_pytest

if is_running_under_pytest():
    # Use test-specific configuration
    pass
```

---

## Mock Utilities

### create_mock_superclass_test

**Type:** Function

**Import from:** `apathetic_testing`

**Signature:**
```python
create_mock_superclass_test(superclass: type) -> type
```

Create a mock subclass for testing inheritance patterns without requiring the full superclass implementation.

**Parameters:**
- `superclass` (type) — The superclass to mock

**Returns:** A mock subclass that can be used in tests

**Example:**
```python
from apathetic_testing import create_mock_superclass_test

class MyBase:
    def required_method(self):
        raise NotImplementedError

# Create a mock for testing
MockBase = create_mock_superclass_test(MyBase)

def test_inheritance():
    # Use MockBase in your tests
    assert issubclass(MockBase, MyBase)
```

---

## Build Utilities

### ensure_stitched_script_up_to_date

**Type:** Function

**Import from:** `apathetic_testing`

**Signature:**
```python
ensure_stitched_script_up_to_date(module_name: str) -> bool
```

Check if the stitched script (generated by serger) is up to date with the source code.

**Returns:** `True` if up to date, `False` otherwise

**Example:**
```python
from apathetic_testing import ensure_stitched_script_up_to_date

if not ensure_stitched_script_up_to_date("my_package"):
    print("Stitched script is out of date. Run: poetry run poe build:stitched")
```

---

### ensure_zipapp_up_to_date

**Type:** Function

**Import from:** `apathetic_testing`

**Signature:**
```python
ensure_zipapp_up_to_date(module_name: str) -> bool
```

Check if the zipapp is up to date with the source code.

**Returns:** `True` if up to date, `False` otherwise

**Example:**
```python
from apathetic_testing import ensure_zipapp_up_to_date

if not ensure_zipapp_up_to_date("my_package"):
    print("Zipapp is out of date. Run: poetry run poe build:zipapp")
```

---

## StreamCapture

**Type:** Context manager (returned by `isolated_logging.capture_streams()`)

Captures log records for message counting. Works reliably in xdist parallel mode and stitched mode, unlike pytest's `caplog`.

**Methods:**
- `count_message(message: str) -> int` — Count exact message occurrences

**Example:**
```python
from apathetic_testing.logging import isolated_logging

def test_no_duplication(isolated_logging):
    logger = isolated_logging.get_logger("myapp")
    logger.setLevel("DEBUG")

    with isolated_logging.capture_streams() as capture:
        logger.debug("unique message")

    count = capture.count_message("unique message")
    assert count == 1  # Not duplicated
```

**Why StreamCapture instead of caplog?**
- Works in xdist parallel mode (caplog may fail in worker processes)
- Works in stitched mode (caplog's handler inspection fails)
- Works with apathetic-logging's handler system
- Consistent across all runtime modes
