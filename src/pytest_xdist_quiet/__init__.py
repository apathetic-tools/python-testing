"""Pytest plugin for xdist-related warning suppression.

This plugin suppresses the pytest-benchmark warning that occurs when running
tests with xdist (parallel tests). The warning "Benchmarks are automatically
disabled because xdist plugin is active" is expected behavior and is hidden by
this plugin for cleaner test output.

To use this plugin, either:

**Option 1: Auto-load via entry point (recommended)**
No setup needed—pytest automatically discovers and loads the plugin when installed.

**Option 2: Manual loading in conftest.py**
```python
pytest_plugins = ["pytest_xdist_quiet"]
```
"""

from __future__ import annotations

from pytest_xdist_quiet.plugin import pytest_configure


__all__ = ["pytest_configure"]
