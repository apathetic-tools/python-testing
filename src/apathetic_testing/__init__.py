# src/apathetic_testing/__init__.py
"""Apathetic utilities package."""

from typing import TYPE_CHECKING, cast


if TYPE_CHECKING:
    from .namespace import apathetic_testing as _apathetic_testing_class

# Get reference to the namespace class
# In stitched mode: class is already defined in namespace.py (executed before this)
# In package mode: import from namespace module
_apathetic_testing_is_standalone = globals().get("__STITCHED__", False)

if _apathetic_testing_is_standalone:
    # Stitched mode: class already defined in namespace.py
    # Get reference to the class (it's already in globals from namespace.py)
    _apathetic_testing_raw = globals().get("apathetic_testing")
    if _apathetic_testing_raw is None:
        # Fallback: should not happen, but handle gracefully
        msg = "apathetic_testing class not found in stitched mode"
        raise RuntimeError(msg)
    # Type cast to help mypy understand this is the apathetic_testing class
    # The import gives us type[apathetic_testing], so cast to
    # type[_apathetic_testing_class]
    apathetic_testing = cast("type[_apathetic_testing_class]", _apathetic_testing_raw)
else:
    # Package mode: import from namespace module
    # This block is only executed in package mode, not in stitched builds
    from .namespace import apathetic_testing

    # Ensure the else block is not empty (build script may remove import)
    _ = apathetic_testing

# Export all namespace items for convenience
# These are aliases to apathetic_testing.*

# Note: In embedded builds, __init__.py is excluded from the stitch,
# so this code never runs and no exports happen (only the class is available).
# In stitched/package builds, __init__.py is included, so exports happen.

# System
ensure_stitched_script_up_to_date = apathetic_testing.ensure_stitched_script_up_to_date
ensure_zipapp_up_to_date = apathetic_testing.ensure_zipapp_up_to_date
runtime_swap = apathetic_testing.runtime_swap

# Testing - Runtime
detect_module_runtime_mode = apathetic_testing.detect_module_runtime_mode

# Testing - Pytest
is_running_under_pytest = apathetic_testing.is_running_under_pytest

# Testing - Mock
create_mock_superclass_test = apathetic_testing.create_mock_superclass_test

# Testing - Patch
patch_everywhere = apathetic_testing.patch_everywhere


__all__ = [  # noqa: RUF022
    # system
    "ensure_stitched_script_up_to_date",
    "ensure_zipapp_up_to_date",
    "runtime_swap",
    # testing - runtime
    "detect_module_runtime_mode",
    # testing - pytest
    "is_running_under_pytest",
    # testing - mock
    "create_mock_superclass_test",
    # testing - patch
    "patch_everywhere",
]
