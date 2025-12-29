---
layout: base
title: Home
permalink: /
---

# Apathetic Python Testing ⚙️

**Grab bag of helpers for Apathetic projects.**  
*When stdlib is almost enough.*

*Apathetic Python Testing* provides a lightweight, dependency-free collection of utility functions designed for CLI tools. It includes helpers for file loading, path manipulation, system detection, text processing, type checking, pattern matching, and more.

## Features
- 🪶 **Zero dependencies** — Uses only Python's standard library (except apathetic-logging for logging)
- 📁 **File loading** — Load TOML and JSONC files with comment support
- 🛤️ **Path utilities** — Cross-platform path normalization and glob handling
- 🔍 **Pattern matching** — Portable glob pattern matching with recursive `**` support
- 🧩 **Module detection** — Detect Python packages from file paths
- 🧪 **System detection** — Detect CI environments, pytest execution, and runtime modes
- ⚙️ **Runtime utilities** — Build and test utilities for stitched scripts and zipapps
- 🔧 **Subprocess utilities** — Capture and forward subprocess output
- 📝 **Text processing** — Pluralization and error message cleanup utilities
- 🔧 **Type utilities** — Safe isinstance checks for TypedDicts and generics
- 🧪 **Testing utilities** — Helpers for testing mixins and patching functions
- 🎯 **CLI-friendly** — Designed with command-line applications in mind
- 🧩 **Apathetic Tools integration** — Works seamlessly with serger and other Apathetic Tools


## Quick Example

```python
from apathetic_testing import load_jsonc, load_toml, is_ci, detect_runtime_mode, capture_output
from pathlib import Path
import sys

# Load configuration files
config = load_jsonc(Path("config.jsonc"))
pyproject = load_toml(Path("pyproject.toml"))

# Detect environment
if is_ci():
    print("Running in CI")

# Detect runtime mode (package, stitched, zipapp, frozen)
mode = detect_runtime_mode("my_package")
print(f"Running in {mode} mode")

# Capture output from CLI commands
with capture_output() as cap:
    # Run some command that prints to stdout/stderr
    print("Hello, world!")
    print("Error message", file=sys.stderr)

print(f"Captured: {cap.merged.getvalue()}")
```

## Requirements

- **Python 3.10+**

No other dependencies required — this library uses only Python's standard library.

## Installation

Install via **poetry** or **pip**:

```bash
# Using poetry
poetry add apathetic-utils

# Using pip
pip install apathetic-utils
```

For alternative installation methods, see the [Installation Guide]({{ '/installation' | relative_url }}).

## Documentation

- **[Installation Guide]({{ '/installation' | relative_url }})** — How to install and set up
- **[Quick Start]({{ '/quickstart' | relative_url }})** — Get up and running in minutes
- **[API Reference]({{ '/api' | relative_url }})** — Complete API documentation
- **[Examples]({{ '/examples' | relative_url }})** — Advanced usage examples
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

