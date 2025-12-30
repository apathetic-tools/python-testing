# Apathetic Python Testing 🧪

[![CI](https://github.com/apathetic-tools/python-testing/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/apathetic-tools/python-testing/actions/workflows/ci.yml)
[![License: MIT-a-NOAI](https://img.shields.io/badge/License-MIT--a--NOAI-blueviolet.svg)](LICENSE)
[![Discord](https://img.shields.io/badge/Discord-%235865F2.svg?logo=discord&logoColor=white)](https://discord.gg/PW6GahZ7)

📘 **[Roadmap](./ROADMAP.md)** · 📝 **[Release Notes](https://github.com/apathetic-tools/python-testing/releases)**

**Runtime-aware pytest extensions.**  
*When you need just a bit more.*

*Apathetic Python Testing* provides a focused collection of pytest fixtures and utilities designed for Apathetic Tools projects. It helps you test CLI applications, logging behavior, and code that ships as stitched scripts or zipapps.

Some ways to generate stitched scripts are [serger](https://github.com/apathetic-tools/serger); and for zipapps: [zipbundler](https://github.com/apathetic-tools/zipbundler) or stdlib's [zipapp](https://docs.python.org/3/library/zipapp.html).

> [!NOTE]
> Heads up: the AI cooked dinner. It's edible, but watch your step.  
> Detailed bug reports welcome.

## Quick Start

```python
from apathetic_testing import patch_everywhere, runtime_swap
from apathetic_testing.logging import (
    isolated_logging,
    logging_test_level,
    logging_level_testing,
)

# Test log level isolation
def test_app_logging(isolated_logging):
    # Each test gets fresh logging state
    isolated_logging.set_root_level("DEBUG")
    my_app.run()

# Debug with maximum verbosity
def test_app_with_debugging(logging_test_level):
    # Root logger at TEST level - all logs visible
    my_app.run()

# Test log level changes
def test_cli_debug_flag(logging_level_testing):
    cli.main(["--log-level", "debug"])
    logging_level_testing.assert_level_changed_from("ERROR", to="DEBUG")

# Safe patching in all runtime modes
from unittest.mock import Mock
with patch_everywhere("module.function", Mock(return_value=42)):
    result = module.function()

# Test stitched/zipapp builds
def test_in_stitched_mode(runtime_swap):
    # Automatically swaps to stitched mode if available
    import my_package
    my_package.function()
```

## Installation

```bash
# Using poetry
poetry add apathetic-testing

# Using pip
pip install apathetic-testing
```

## Documentation

📚 **[Full Documentation →](https://apathetic-tools.github.io/python-testing/)**

For installation guides, API reference, examples, and more, visit our documentation website.

## Features

- **🔍 Logging Fixtures** — Isolated logging state, TEST level debugging, level change assertions
- **🎯 Safe Patching** — `patch_everywhere` for reliable mocking in package, stitched, and zipapp modes
- **🔄 Runtime Testing** — `runtime_swap` to test stitched scripts and zipapp builds
- **🪶 Lightweight** — Minimal dependencies (only apathetic-logging)
- **🧪 CLI-Focused** — Designed for testing command-line applications and config-driven tools
- **🔧 Helper Utilities** — Mock superclass detection, assertion helpers, and more

---

## ⚖️ License

- [MIT-a-NOAI License](LICENSE)

You're free to use, copy, and modify the library under the standard MIT terms.  
The additional rider simply requests that this project not be used to train or fine-tune AI/ML systems until the author deems fair compensation frameworks exist.  
Normal use, packaging, and redistribution for human developers are unaffected.
