"""Pytest plugin for apathetic logging fixtures.

This plugin automatically registers logging fixtures for pytest:
- atest_reset_logger_level (autouse - runs for every test)
- atest_apathetic_logger
- atest_isolated_logging
- atest_logging_level_testing
- atest_logging_test_level

To use this plugin, install both apathetic-testing and pytest-apathetic-logging,
then either:

**Option 1: Auto-load via entry point (recommended)**
No setup needed—pytest automatically discovers and loads the plugin when installed.

**Option 2: Manual loading in conftest.py**
```python
pytest_plugins = ["pytest_apathetic_logging"]
```
"""

from __future__ import annotations

import apathetic_testing as alib_test


# Re-export fixtures for pytest discovery
# These will be automatically discovered when pytest loads this plugin
atest_reset_logger_level = alib_test.atest_reset_logger_level
atest_apathetic_logger = alib_test.atest_apathetic_logger
atest_isolated_logging = alib_test.atest_isolated_logging
atest_logging_level_testing = alib_test.atest_logging_level_testing
atest_logging_test_level = alib_test.atest_logging_test_level


__all__ = [
    "atest_apathetic_logger",
    "atest_isolated_logging",
    "atest_logging_level_testing",
    "atest_logging_test_level",
    "atest_reset_logger_level",
]
