# src/apathetic_testing/__init__.py
"""Apathetic utilities package."""

from typing import TYPE_CHECKING, TypeAlias, cast


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

# CI
CI_ENV_VARS = apathetic_testing.CI_ENV_VARS
if_ci = apathetic_testing.if_ci
is_ci = apathetic_testing.is_ci

# Files
load_jsonc = apathetic_testing.load_jsonc
load_toml = apathetic_testing.load_toml

# Matching
fnmatchcase_portable = apathetic_testing.fnmatchcase_portable
is_excluded_raw = apathetic_testing.is_excluded_raw

# Modules
detect_packages_from_files = apathetic_testing.detect_packages_from_files
find_all_packages_under_path = apathetic_testing.find_all_packages_under_path

# Paths
get_glob_root = apathetic_testing.get_glob_root
has_glob_chars = apathetic_testing.has_glob_chars
normalize_path_string = apathetic_testing.normalize_path_string
shorten_path = apathetic_testing.shorten_path

# System
# CapturedOutput is a nested class in ApatheticUtils_Internal_Subprocess that
# is accessed via the namespace class.
# Use TypeAlias to help mypy understand this is a class type.
if TYPE_CHECKING:
    from .subprocess_utils import ApatheticUtils_Internal_Subprocess

    CapturedOutput: TypeAlias = ApatheticUtils_Internal_Subprocess.CapturedOutput
else:
    CapturedOutput = apathetic_testing.CapturedOutput

capture_output = apathetic_testing.capture_output
create_version_info = apathetic_testing.create_version_info
detect_runtime_mode = apathetic_testing.detect_runtime_mode
ensure_stitched_script_up_to_date = apathetic_testing.ensure_stitched_script_up_to_date
ensure_zipapp_up_to_date = apathetic_testing.ensure_zipapp_up_to_date
find_python_command = apathetic_testing.find_python_command
get_sys_version_info = apathetic_testing.get_sys_version_info
is_running_under_pytest = apathetic_testing.is_running_under_pytest
run_with_output = apathetic_testing.run_with_output
run_with_separated_output = apathetic_testing.run_with_separated_output
runtime_swap = apathetic_testing.runtime_swap

# Testing
create_mock_superclass_test = apathetic_testing.create_mock_superclass_test
detect_module_runtime_mode = apathetic_testing.detect_module_runtime_mode
patch_everywhere = apathetic_testing.patch_everywhere

# Text
plural = apathetic_testing.plural
remove_path_in_error_message = apathetic_testing.remove_path_in_error_message

# Types
cast_hint = apathetic_testing.cast_hint
literal_to_set = apathetic_testing.literal_to_set
safe_isinstance = apathetic_testing.safe_isinstance
schema_from_typeddict = apathetic_testing.schema_from_typeddict


__all__ = [  # noqa: RUF022
    # ci
    "CI_ENV_VARS",
    "if_ci",
    "is_ci",
    # files
    "load_jsonc",
    "load_toml",
    # matching
    "fnmatchcase_portable",
    "is_excluded_raw",
    # modules
    "detect_packages_from_files",
    "find_all_packages_under_path",
    # paths
    "get_glob_root",
    "has_glob_chars",
    "normalize_path_string",
    "shorten_path",
    # system
    "CapturedOutput",
    "capture_output",
    "create_version_info",
    "detect_runtime_mode",
    "ensure_stitched_script_up_to_date",
    "ensure_zipapp_up_to_date",
    "find_python_command",
    "get_sys_version_info",
    "is_running_under_pytest",
    "run_with_output",
    "run_with_separated_output",
    "runtime_swap",
    # testing
    "create_mock_superclass_test",
    "detect_module_runtime_mode",
    "patch_everywhere",
    # text
    "plural",
    "remove_path_in_error_message",
    # types
    "cast_hint",
    "literal_to_set",
    "safe_isinstance",
    "schema_from_typeddict",
]
