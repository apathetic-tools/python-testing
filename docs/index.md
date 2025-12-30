---
layout: base
title: Home
permalink: /
---

# Apathetic Python Testing 🧪

**Runtime-aware pytest extensions.**  
*When you need just a bit more.*

*Apathetic Python Testing* provides a focused collection of pytest fixtures and utilities designed for Apathetic Tools projects. It helps you test CLI applications, logging behavior, and code that ships as stitched scripts or zipapps.

Some ways to generate stitched scripts are [serger](https://github.com/apathetic-tools/serger); and for zipapps: [zipbundler](https://github.com/apathetic-tools/zipbundler) or stdlib's [zipapp](https://docs.python.org/3/library/zipapp.html).

## Features

- **🔍 Logging Fixtures** — Isolated logging state, TEST level debugging, level change assertions
- **🎯 Safe Patching** — `patch_everywhere` for reliable mocking in package, stitched, and zipapp modes
- **🔄 Runtime Testing** — `runtime_swap` to test stitched scripts and zipapp builds
- **🪶 Lightweight** — Minimal dependencies (only apathetic-logging)
- **🧪 CLI-Focused** — Designed for testing command-line applications and config-driven tools
- **🔧 Helper Utilities** — Mock superclass detection, assertion helpers, and more


## Quick Example

```python
from apathetic_testing import patch_everywhere
from apathetic_testing.logging import (
    isolated_logging,
    logging_test_level,
    logging_level_testing,
)
from unittest.mock import Mock

# Test with isolated logging
def test_app_logging(isolated_logging):
    isolated_logging.set_root_level("DEBUG")
    my_app.run()
    # State automatically reset after test

# Debug with TEST level (all logs visible)
def test_app_with_debugging(logging_test_level):
    my_app.run()  # All DEBUG and TRACE logs visible

# Test log level changes (e.g., --log-level flag)
def test_cli_debug_flag(logging_level_testing):
    cli.main(["--log-level", "debug"])
    logging_level_testing.assert_level_changed_from("ERROR", to="DEBUG")

# Safe patching that works in all runtime modes
def test_with_patching():
    with patch_everywhere("module.function", Mock(return_value=42)):
        result = module.function()
        assert result == 42
```

## Requirements

- **Python 3.10+**

No other dependencies required — this library uses only Python's standard library.

## Installation

Install via **poetry** or **pip**:

```bash
# Using poetry
poetry add apathetic-testing

# Using pip
pip install apathetic-testing
```

## Documentation

- **[Usage Guide]({{ '/usage' | relative_url }})** — Integration patterns and best practices
- **[API Reference]({{ '/reference' | relative_url }})** — Complete API documentation
- **[Pytest Plugins]({{ '/pytest-plugins' | relative_url }})** — Built-in plugins documentation
- **[Contributing]({{ '/contributing' | relative_url }})** — How to contribute

## License

[MIT-a-NOAI License](https://github.com/apathetic-tools/python-testing/blob/main/LICENSE)

You're free to use, copy, and modify the library under the standard MIT terms.  
The additional rider simply requests that this project not be used to train or fine-tune AI/ML systems until the author deems fair compensation frameworks exist.  
Normal use, packaging, and redistribution for human developers are unaffected.

## Resources

- 📘 [Roadmap](https://github.com/apathetic-tools/python-testing/blob/main/ROADMAP.md)
- 📝 [Release Notes](https://github.com/apathetic-tools/python-testing/releases)
- 🐛 [Issue Tracker](https://github.com/apathetic-tools/python-testing/issues)
- 💬 [Discord](https://discord.gg/PW6GahZ7)

