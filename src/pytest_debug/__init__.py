"""Pytest plugin for filtering debug-marked tests.

This plugin automatically hides tests marked with @pytest.mark.debug from the
normal test run, making them opt-in only. To run debug tests, use:

    pytest -k debug

To use this plugin, either:

**Option 1: Auto-load via entry point (recommended)**
No setup needed—pytest automatically discovers and loads the plugin when installed.

**Option 2: Manual loading in conftest.py**
```python
pytest_plugins = ["pytest_debug"]
```
"""

from __future__ import annotations

from pytest_debug.plugin import pytest_collection_modifyitems


__all__ = ["pytest_collection_modifyitems"]
