# tests/conftest.py
"""Shared test setup for project.

Each pytest run now targets a single runtime mode:
- Package mode (default): uses src/<package> when RUNTIME_MODE=package
- Stitched mode: uses dist/<package>.py when RUNTIME_MODE=stitched
- Zipapp mode: uses dist/<package>.pyz when RUNTIME_MODE=zipapp

Switch mode with: RUNTIME_MODE=stitched pytest or RUNTIME_MODE=zipapp pytest
"""

import apathetic_testing as alib_test


# early jank hook, must happen before importing the <package>
# so we get the stitched/zipapp version in the right mode
alib_test.runtime_swap()

# Load plugins that provide fixtures and hooks
# - pytest_apathetic_logging: logging fixtures (atest_reset_logger_level autouse)
# - pytest_debug: filters @pytest.mark.debug tests (opt-in via -k debug)
# - pytest_quiet: adjusts output based on verbosity level
# - pytest_runtime: runtime mode filtering and reporting
pytest_plugins = [
    "pytest_apathetic_logging",
    "pytest_debug",
    "pytest_quiet",
    "pytest_runtime",
]
