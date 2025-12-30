"""Pytest plugin for default timeout configuration.

This plugin sets a default timeout of 60 seconds for all tests, but only if the
user hasn't already configured a timeout via pytest configuration, command line,
or environment variables.

To use this plugin, either:

**Option 1: Auto-load via entry point (recommended)**
No setup needed—pytest automatically discovers and loads the plugin when installed.

**Option 2: Manual loading in conftest.py**
```python
pytest_plugins = ["pytest_timeout"]
```
"""

from __future__ import annotations

from pytest_timeout_defaults.plugin import pytest_configure


__all__ = ["pytest_configure"]
