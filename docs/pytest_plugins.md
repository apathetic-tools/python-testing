---
layout: base
title: Pytest Plugins
permalink: /pytest-plugins/
---

# Pytest Plugins

Documentation for the pytest plugins included with `apathetic-testing`.

## Overview

When you install `apathetic-testing`, several pytest plugins are automatically registered and loaded:

- **`pytest_timeout_defaults`** — Provides sensible timeout defaults
- **`pytest_xdist_quiet`** — Suppresses benchmark warnings when running with xdist
- **`pytest_apathetic_logging`** — Provides logging fixtures (see [Usage Guide](/usage/))
- **`pytest_debug`** — Filters `@pytest.mark.debug` tests
- **`pytest_quiet`** — Adjusts output verbosity
- **`pytest_runtime`** — Runtime mode reporting

This page documents the first two plugins. For logging, debug, and quiet features, see the [Usage Guide](/usage/).

## Table of Contents

1. [pytest_timeout_defaults](#pytest_timeout_defaults)
2. [pytest_xdist_quiet](#pytest_xdist_quiet)
3. [Disabling Plugins](#disabling-plugins)
4. [Helper Functions](#helper-functions)

---

## pytest_timeout_defaults

### Purpose

Provides sensible default timeout configuration for pytest when the `pytest-timeout` plugin is installed. This plugin automatically configures:

- **Timeout:** 60 seconds (default timeout for all tests)
- **timeout_func_only:** False (applies timeout to all tests, not just functions)

### Behavior

The plugin respects user configuration and only applies defaults when the user hasn't explicitly configured these values. Users can override the defaults via:

1. **Configuration file:** `pytest.ini` or `pyproject.toml`
   ```ini
   [pytest]
   timeout = 120
   timeout_func_only = True
   ```

2. **Environment variables:** `PYTEST_TIMEOUT=120`

3. **CLI flags:** `--timeout=120 --timeout-func-only`

### When It Applies

The plugin automatically applies defaults **only when**:
- The `pytest-timeout` plugin is installed and active
- The user has **not** configured timeout via any method (config file, env var, or CLI)
- The user has **not** configured timeout_func_only via any method

### Example: Default Timeout

Without any configuration, tests will timeout after 60 seconds:

```python
# This test will timeout after 60 seconds (default)
def test_long_operation():
    result = expensive_operation()
    assert result.success
```

### Example: Overriding the Default

Override the default timeout via `pytest.ini`:

```ini
[pytest]
timeout = 120
```

Or via CLI:

```bash
pytest --timeout=120
```

Or via environment variable:

```bash
PYTEST_TIMEOUT=120 pytest
```

### Detecting User Configuration

The plugin uses a helper function `has_pytest_user_config()` from the `apathetic_testing` library to check if a user has configured an option. See [Helper Functions](#helper-functions) for details.

---

## pytest_xdist_quiet

### Purpose

Suppresses benchmark warning messages when running tests with pytest-xdist parallel execution. This plugin adds a filter to suppress `BenchmarkWarning` messages that would otherwise clutter the output.

### Behavior

The plugin automatically suppresses benchmark warnings **only when**:
- The `pytest-xdist` plugin is installed and active
- The `pytest-benchmark` plugin is installed and active
- The filter hasn't already been configured by the user

### When It Applies

When running tests in parallel with xdist, benchmark warnings are filtered out to keep the output clean:

```bash
# Warnings will be filtered silently
pytest -n auto
```

### Example: Parallel Testing Without Benchmark Noise

```python
# test_performance.py
import pytest

def test_quick_operation(benchmark):
    """This test runs in parallel with xdist."""
    def run_operation():
        return sum(range(1000))

    result = benchmark(run_operation)
    assert result > 0
```

Run with xdist to see clean output without benchmark warnings:

```bash
pytest -n auto
```

### Disabling the Filter

If you want to see benchmark warnings, add your own filterwarnings configuration:

```ini
[pytest]
filterwarnings =
    error::pytest_benchmark.BenchmarkWarning
```

Or via CLI:

```bash
pytest -W error::pytest_benchmark.BenchmarkWarning
```

---

## Disabling Plugins

You can disable one or more plugins if desired.

### Via pytest.ini

Add to your `pytest.ini` to disable plugins:

```ini
[pytest]
addopts = -p no:pytest_timeout_defaults
          -p no:pytest_xdist_quiet
          -p no:pytest_apathetic_logging
          -p no:pytest_debug
          -p no:pytest_quiet
          -p no:pytest_runtime
```

### Via Command Line

Disable plugins at runtime:

```bash
pytest -p no:pytest_timeout_defaults -p no:pytest_xdist_quiet
```

### Via Environment Variable

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest
```

### Selective Disabling

You can disable only the plugins you don't want while keeping others:

```ini
[pytest]
# Disable only timeout defaults and xdist quiet
addopts = -p no:pytest_timeout_defaults -p no:pytest_xdist_quiet
```

---

## Helper Functions

### has_pytest_user_config()

**Type:** Static method on `ApatheticTest_Internal_Pytest` mixin class

**Import from:** `apathetic_testing.pytest`

**Signature:**
```python
@staticmethod
def has_pytest_user_config(config: pytest.Config, option_name: str) -> bool
```

**Purpose:** Determine if a pytest option has been configured by the user via any method.

**Parameters:**
- `config` — The pytest Config object (passed to pytest hooks)
- `option_name` — Name of the option to check (e.g., `"timeout"`, `"markers"`)

**Returns:** `True` if the user has configured the option, `False` otherwise

**Configuration Sources Checked (in order):**

1. **Config file and environment variables** via `config.getini(option_name)`
   - Checks `pytest.ini` / `pyproject.toml` settings
   - Also checks environment variables (e.g., `PYTEST_TIMEOUT`)

2. **CLI flags** via `config.getoption(option_name)`
   - Checks command-line arguments like `--timeout=60`

### How It's Used

The plugin uses this function internally to determine whether to apply defaults:

```python
user_configured_timeout = ApatheticTest_Internal_Pytest.has_pytest_user_config(
    config, "timeout"
)

if not user_configured_timeout:
    # Apply our defaults
    config.inicfg["timeout"] = 60
```

### Using It In Your Own Code

You can use this function in custom pytest plugins or test hooks:

```python
import apathetic_testing.pytest as ap_pytest

def pytest_configure(config):
    """Your custom pytest plugin."""
    has_custom_timeout = ap_pytest.ApatheticTest_Internal_Pytest.has_pytest_user_config(
        config, "timeout"
    )

    if not has_custom_timeout:
        # Apply your own defaults
        config.inicfg["timeout"] = 300
```

### Example: Checking Multiple Options

Check if multiple options are configured:

```python
from apathetic_testing.pytest import ApatheticTest_Internal_Pytest

def check_options(config):
    """Check which options the user has configured."""
    options = ["timeout", "timeout_func_only", "markers"]

    for option_name in options:
        is_configured = ApatheticTest_Internal_Pytest.has_pytest_user_config(
            config, option_name
        )
        print(f"{option_name}: {'configured' if is_configured else 'not configured'}")
```

### Edge Cases

The function handles several edge cases gracefully:

- **Missing options:** Returns `False` if the option doesn't exist
- **KeyError/ValueError:** Catches and continues checking other sources
- **Falsy but configured values:** Treats any truthy value as configured (0, empty string, etc. are considered not configured)
- **Multiple sources:** If any source has the option, returns `True`

---

## Common Patterns

### Combining Timeout and xdist

Use both plugins together for reliable parallel testing with timeouts:

```bash
pytest -n auto
```

This runs tests in parallel (via `pytest_xdist_quiet` suppressing warnings) with a 60-second timeout per test (via `pytest_timeout_defaults`).

### Custom Plugins Using the Helper

Create a custom pytest plugin that respects user overrides:

```python
# conftest.py
import apathetic_testing.pytest as ap_pytest

def pytest_configure(config):
    """Apply custom defaults only if user hasn't configured."""
    if not ap_pytest.ApatheticTest_Internal_Pytest.has_pytest_user_config(
        config, "custom_option"
    ):
        config.inicfg["custom_option"] = "my_value"
```

### Testing With Timeouts

Write tests that work with the default 60-second timeout:

```python
import pytest

def test_normal_operation():
    """This test will timeout after 60 seconds."""
    result = my_function()
    assert result is not None

@pytest.mark.timeout(300)  # Override for slow tests
def test_slow_operation():
    """This test gets 300 seconds (override default)."""
    result = expensive_operation()
    assert result is not None
```

---

## Next Steps

- **[Usage Guide](/usage/)** — Integration patterns and examples
- **[API Reference](/reference/)** — Complete API documentation
