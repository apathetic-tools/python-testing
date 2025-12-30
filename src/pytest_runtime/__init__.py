"""Pytest plugin for runtime mode filtering and reporting.

This plugin manages test filtering based on runtime mode (package, stitched, zipapp)
and provides reporting for mode-specific tests. It works alongside the test's
__runtime_mode__ marker to include/exclude tests based on the current mode.

To use this plugin, either:

**Option 1: Auto-load via entry point (recommended)**
No setup needed—pytest automatically discovers and loads the plugin when installed.

**Option 2: Manual loading in conftest.py**
```python
pytest_plugins = ["pytest_runtime"]
```
"""

from __future__ import annotations

from pytest_runtime.plugin import (
    pytest_addoption,
    pytest_collection_modifyitems,
    pytest_report_header,
    pytest_unconfigure,
)


__all__ = [
    "pytest_addoption",
    "pytest_collection_modifyitems",
    "pytest_report_header",
    "pytest_unconfigure",
]
