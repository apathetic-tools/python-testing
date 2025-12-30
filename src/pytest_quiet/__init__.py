"""Pytest plugin for quiet mode output suppression.

This plugin automatically adjusts pytest's report output based on verbosity level.
In quiet mode (default), skipped tests and extra output are hidden for cleaner output.

To use this plugin, either:

**Option 1: Auto-load via entry point (recommended)**
No setup needed—pytest automatically discovers and loads the plugin when installed.

**Option 2: Manual loading in conftest.py**
```python
pytest_plugins = ["pytest_quiet"]
```
"""

from __future__ import annotations

from pytest_quiet.plugin import pytest_configure


__all__ = ["pytest_configure"]
