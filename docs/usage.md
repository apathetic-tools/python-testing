---
layout: base
title: Usage Guide
permalink: /usage/
---

# Usage Guide

Integration patterns and examples for Apathetic Python Testing fixtures and utilities.

## Table of Contents

1. [Basic Integration](#basic-integration)
2. [Disabling Pytest Plugins](#disabling-pytest-plugins)
3. [Testing with Isolated Logging](#testing-with-isolated-logging)
4. [Debugging with TEST Level](#debugging-with-test-level)
5. [Testing Log Level Changes](#testing-log-level-changes)
6. [Safe Patching](#safe-patching)
7. [Testing Runtime Modes](#testing-runtime-modes)
8. [Mock Superclass Testing](#mock-superclass-testing)
9. [Common Patterns](#common-patterns)
10. [Best Practices](#best-practices)

## Basic Integration

### Importing Fixtures and Utilities

The main utilities are pytest fixtures for testing logging behavior, patching, and runtime modes. Import them directly in your test files:

```python
from apathetic_testing import patch_everywhere, runtime_swap
from apathetic_testing.logging import (
    isolated_logging,
    logging_test_level,
    logging_level_testing,
)

def test_example(isolated_logging):
    # Use the fixture in your test
    pass
```

### Adding to conftest.py

For project-wide access without importing in every test file, add to your `tests/conftest.py`:

```python
# tests/conftest.py
pytest_plugins = [
    "apathetic_testing.logging",
]
```

This registers all fixtures from the module automatically.

## Disabling Pytest Plugins

When you install `apathetic-testing`, four pytest plugins are automatically loaded via entry points:

- `pytest_apathetic_logging` — Logging fixtures and autouse logger reset
- `pytest_debug` — Filters tests marked with `@pytest.mark.debug`
- `pytest_quiet` — Adjusts output verbosity
- `pytest_runtime` — Runtime mode reporting

### Opting Out via pytest.ini

If you want to disable one or more plugins, add to your `pytest.ini`:

```ini
[pytest]
addopts = -p no:pytest_apathetic_logging
          -p no:pytest_debug
          -p no:pytest_quiet
          -p no:pytest_runtime
```

You can selectively disable individual plugins as needed. For example, to keep logging fixtures but disable debug filtering:

```ini
[pytest]
addopts = -p no:pytest_debug -p no:pytest_quiet
```

### Other Opt-Out Methods

- **Command line**: `pytest --disable-plugin-autoload`
- **Environment variable**: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest`
- **conftest.py**: Set `pytest_plugins = []` or list only plugins you want

## Testing with Isolated Logging

### Basic Logging Isolation

Use `isolated_logging` to get a fresh logging state for each test. The fixture automatically saves and restores the complete logging configuration:

```python
from apathetic_testing.logging import isolated_logging

def test_logger_isolation(isolated_logging):
    # Each test gets fresh, isolated logging state
    isolated_logging.set_root_level("DEBUG")

    # Your test code here
    my_app.run()

    # State is automatically reset after test
```

### Setting Up Loggers in Tests

Get and configure loggers for your tests:

```python
from apathetic_testing.logging import isolated_logging

def test_logger_setup(isolated_logging):
    """Configure multiple loggers for testing."""
    # Get loggers for different modules
    app_logger = isolated_logging.get_logger("myapp")
    util_logger = isolated_logging.get_logger("myapp.utils")

    # Set levels independently
    app_logger.setLevel("INFO")
    util_logger.setLevel("DEBUG")

    # Use them in your tests
    app_logger.info("app message")
    util_logger.debug("util message")
```

### Capturing Log Messages

Capture and verify log output without relying on pytest's `caplog`:

```python
from apathetic_testing.logging import isolated_logging

def test_log_message_count(isolated_logging):
    """Verify log messages are not duplicated."""
    logger = isolated_logging.get_logger("myapp")
    logger.setLevel("DEBUG")

    with isolated_logging.capture_streams() as capture:
        logger.debug("processing file")
        logger.debug("processing file")

    # Verify message count
    count = capture.count_message("processing file")
    assert count == 2
```

**Why StreamCapture instead of pytest's caplog?**
- Works reliably in xdist parallel mode (caplog may fail in worker processes)
- Works in stitched/zipapp builds (caplog's handler inspection fails)
- Compatible with apathetic-logging's handler system
- Consistent across all runtime modes

## Debugging with TEST Level

### Maximum Verbosity for Debugging

Use `logging_test_level` to see all logs including DEBUG and TRACE when tests fail:

```python
from apathetic_testing.logging import logging_test_level

def test_complex_operation(logging_test_level):
    """Get maximum log output for debugging."""
    # Root logger automatically set to TEST level (most verbose)
    result = complex_operation()

    # All DEBUG and TRACE logs visible even if test fails
    assert result is not None
```

The TEST level (value 2) is more verbose than DEBUG and bypasses pytest's capsys to write to `sys.__stderr__`, ensuring logs appear even when output is captured.

### Allowing Dynamic Level Changes

When debugging, you can temporarily allow the app to change log levels:

```python
from apathetic_testing.logging import logging_test_level

def test_with_dynamic_levels(logging_test_level):
    """Allow the app to modify log levels while debugging."""
    # Temporarily allow level changes
    with logging_test_level.temporarily_allow_changes():
        app.set_log_level("TRACE")
        result = app.run()

    # Changes prevented again outside the context manager
    assert result is not None
```

## Testing Log Level Changes

### Basic Log Level Testing

Verify your app correctly changes log levels in response to CLI arguments or configuration:

```python
from apathetic_testing.logging import logging_level_testing
import pytest

@pytest.mark.initial_level("ERROR")
def test_verbose_flag(logging_level_testing):
    """Test that --verbose flag correctly changes log level."""
    cli.main(["--verbose"])

    # Assert the transition happened
    logging_level_testing.assert_level_changed_from("ERROR", to="DEBUG")
```

### Testing Multiple Level Changes

Track and verify a sequence of log level changes:

```python
from apathetic_testing.logging import logging_level_testing
import pytest

@pytest.mark.initial_level("WARNING")
def test_level_progression(logging_level_testing):
    """Test that app correctly changes log levels in sequence."""
    # Simulate user adjusting log level multiple times
    app.set_log_level("INFO")
    app.set_log_level("DEBUG")

    # Check history
    history = logging_level_testing.get_level_history()
    assert len(history) == 2
```

### Testing Quiet Mode

Verify that quiet/silent mode increases the log level appropriately:

```python
from apathetic_testing.logging import logging_level_testing
import pytest

@pytest.mark.initial_level("INFO")
def test_quiet_mode(logging_level_testing):
    """Test that quiet mode reduces verbosity."""
    cli.main(["--quiet"])

    # Verify it increased to WARNING or higher
    logging_level_testing.assert_root_level("WARNING")
```

## Safe Patching

### Reliable Mocking Across Runtime Modes

Use `patch_everywhere` for mocking that works in package, stitched, and zipapp modes:

```python
from apathetic_testing import patch_everywhere
from unittest.mock import Mock

def test_with_safe_patch():
    """Use patch_everywhere for reliable mocking in all runtime modes."""
    mock_func = Mock(return_value=42)

    with patch_everywhere("mymodule.expensive_operation", mock_func):
        result = mymodule.expensive_operation()
        assert result == 42
        mock_func.assert_called_once()
```

**Why not use unittest.mock.patch?**
- Standard `patch()` uses module import inspection that fails in stitched/zipapp modes
- `patch_everywhere()` handles all runtime modes: package, stitched, and zipapp
- Guarantees consistent behavior across all distribution formats

### Patching External Dependencies

Mock external APIs and dependencies:

```python
from apathetic_testing import patch_everywhere
from unittest.mock import Mock
import pytest

def test_api_failure_handling():
    """Test graceful handling of API failures."""
    mock_api = Mock(side_effect=ConnectionError("API unavailable"))

    with patch_everywhere("requests.get", mock_api):
        with pytest.raises(ConnectionError):
            myapp.fetch_data()
```

### Complex Patching Scenarios

Combine multiple patches safely:

```python
from apathetic_testing import patch_everywhere
from unittest.mock import Mock

def test_multiple_patches():
    """Combine multiple patches safely."""
    with patch_everywhere("module1.func1", Mock(return_value="a")):
        with patch_everywhere("module2.func2", Mock(return_value="b")):
            result = orchestrator.run()
            assert result == ("a", "b")
```

## Testing Runtime Modes

### Testing Against Stitched Builds

Use `runtime_swap` to test your code against stitched builds if available:

```python
from apathetic_testing import runtime_swap

def test_in_stitched_mode(runtime_swap):
    """Test code against stitched build if available."""
    import mypackage

    # This import uses stitched version if available,
    # otherwise falls back to package mode
    result = mypackage.get_version()
    assert result is not None
```

### Verifying Distribution Compatibility

Check which runtime mode the module is running in:

```python
from apathetic_testing import runtime_swap, detect_module_runtime_mode

def test_distribution_compat(runtime_swap):
    """Verify code works in current runtime mode."""
    import mypackage

    mode = detect_module_runtime_mode("mypackage")
    print(f"Testing in {mode} mode")

    # Run compatibility checks
    result = mypackage.run()
    assert result.success
```

The mode will be one of: `"package"`, `"stitched"`, or `"zipapp"`.

## Mock Superclass Testing

### Testing Inheritance Patterns

Create mock base classes for testing subclass logic without full superclass implementation:

```python
from apathetic_testing import create_mock_superclass_test

class MyBase:
    def required_method(self):
        raise NotImplementedError

    def helper_method(self):
        return "base"

def test_subclass_logic():
    """Test a subclass without full superclass implementation."""
    # Create mock base for testing
    MockBase = create_mock_superclass_test(MyBase)

    class MySubclass(MockBase):
        def required_method(self):
            return "implemented"

    obj = MySubclass()
    assert obj.required_method() == "implemented"
    assert issubclass(MySubclass, MyBase)
```

### Isolating Subclass Behavior

Skip expensive superclass logic while testing subclass transformations:

```python
from apathetic_testing import create_mock_superclass_test

class DataProcessor:
    def validate(self, data):
        raise NotImplementedError

    def process(self, data):
        # Complex validation logic in superclass
        self.validate(data)
        return self._transform(data)

def test_transform_logic():
    """Test transformation without complex validation."""
    MockProcessor = create_mock_superclass_test(DataProcessor)

    class SimpleProcessor(MockProcessor):
        def validate(self, data):
            pass  # Skip expensive validation

        def _transform(self, data):
            return data.upper()

    proc = SimpleProcessor()
    result = proc.process("hello")
    assert result == "HELLO"
```

## Common Patterns

### Testing CLI Applications with Log Levels

A common pattern for CLI tools is to have `--verbose` and `--quiet` flags that adjust logging:

```python
from apathetic_testing.logging import logging_level_testing, isolated_logging
import pytest

@pytest.mark.initial_level("INFO")
def test_verbose_flag_enables_debug(logging_level_testing):
    """Verify --verbose enables DEBUG logging."""
    my_cli.main(["--verbose"])
    logging_level_testing.assert_level_changed_from("INFO", to="DEBUG")

@pytest.mark.initial_level("INFO")
def test_quiet_flag_suppresses_info(logging_level_testing):
    """Verify --quiet disables INFO logging."""
    my_cli.main(["--quiet"])
    logging_level_testing.assert_level_changed_from("INFO", to="WARNING")
```

### Testing with Mocking and Logging Isolation

Combine multiple utilities in a single test:

```python
from apathetic_testing import patch_everywhere
from apathetic_testing.logging import isolated_logging
from unittest.mock import Mock

def test_app_with_isolated_logging(isolated_logging):
    """Test app behavior with controlled logging and mocking."""
    isolated_logging.set_root_level("DEBUG")

    with patch_everywhere("myapp.expensive_query", Mock(return_value=[])):
        with isolated_logging.capture_streams() as capture:
            result = my_app.process_data()

    assert result.success
    msg_count = capture.count_message("Processing complete")
    assert msg_count >= 1
```

### Testing Against Multiple Runtime Modes

Verify your code works in all distribution modes:

```python
from apathetic_testing import runtime_swap, patch_everywhere
from unittest.mock import Mock

def test_in_all_modes(runtime_swap):
    """Test code reliably works across package, stitched, and zipapp."""
    # Mock works reliably in all modes
    with patch_everywhere("mymodule.query_db", Mock(return_value=[])):
        import mypackage
        result = mypackage.get_cached_data()
        assert result == []
```

## Best Practices

### 1. Use Isolated Logging for Clean Tests

Always use `isolated_logging` when testing code that configures logging:

```python
# Good: Fresh logging state for each test
def test_my_feature(isolated_logging):
    isolated_logging.set_root_level("DEBUG")
    my_app.run()

# Problematic: Global state can leak between tests
def test_my_feature():
    # May interfere with other tests if logging isn't reset
    import logging
    logging.getLogger().setLevel("DEBUG")
```

### 2. Use logging_level_testing for CLI Arguments

When testing log level CLI arguments, use the fixture with marks:

```python
# Good: Explicit initial state, assertion of transition
@pytest.mark.initial_level("ERROR")
def test_verbose_flag(logging_level_testing):
    cli.main(["--verbose"])
    logging_level_testing.assert_level_changed_from("ERROR", to="DEBUG")

# Problematic: Harder to reason about state
def test_verbose_flag():
    import logging
    cli.main(["--verbose"])
    assert logging.getLogger().level == logging.DEBUG
```

### 3. Use patch_everywhere Instead of unittest.mock.patch

When mocking in tests that might run in stitched/zipapp mode:

```python
# Good: Works in all runtime modes
from apathetic_testing import patch_everywhere

def test_my_feature():
    with patch_everywhere("mymodule.function", Mock()):
        pass

# Problematic: Fails in stitched/zipapp modes
from unittest.mock import patch

def test_my_feature():
    with patch("mymodule.function", Mock()):
        pass
```

### 4. Capture Logs with StreamCapture

Use `isolated_logging.capture_streams()` instead of pytest's `caplog`:

```python
# Good: Works in all runtime modes and xdist parallel
def test_logging_output(isolated_logging):
    logger = isolated_logging.get_logger("myapp")
    logger.setLevel("DEBUG")

    with isolated_logging.capture_streams() as capture:
        logger.info("message")

    assert capture.count_message("message") == 1

# Problematic: Fails in xdist parallel and stitched mode
def test_logging_output(caplog):
    logger = logging.getLogger("myapp")
    logger.info("message")
    assert "message" in caplog.text
```

### 5. Use logging_test_level for Debugging

When you need to see all logs during test failures:

```python
# Good: Maximum verbosity when debugging
def test_complex_operation(logging_test_level):
    result = complex_operation()
    # All TRACE and DEBUG logs visible if test fails

# Problematic: May not show enough logs when debugging
def test_complex_operation():
    my_operation()
```

## Next Steps

- **[API Reference]({{ '/reference' | relative_url }})** — Complete API documentation
- **[Contributing]({{ '/contributing' | relative_url }})** — Learn how to contribute
