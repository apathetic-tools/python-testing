from apathetic_testing.fixtures import (
    ApatheticTest_Internal_Fixtures,
    atest_apathetic_logger,
    atest_isolated_logging,
    atest_logging_level_testing,
    atest_logging_test_level,
    atest_reset_logger_level,
)
from apathetic_testing.namespace import apathetic_testing

# Re-export nested classes at package level
LoggingIsolation = ApatheticTest_Internal_Fixtures.LoggingIsolation
LoggingTestLevel = ApatheticTest_Internal_Fixtures.LoggingTestLevel
LoggingLevelTesting = ApatheticTest_Internal_Fixtures.LoggingLevelTesting

# Re-export all items from apathetic_testing class for convenience
ensure_stitched_script_up_to_date = apathetic_testing.ensure_stitched_script_up_to_date
ensure_zipapp_up_to_date = apathetic_testing.ensure_zipapp_up_to_date
runtime_swap = apathetic_testing.runtime_swap
detect_module_runtime_mode = apathetic_testing.detect_module_runtime_mode
is_running_under_pytest = apathetic_testing.is_running_under_pytest
has_pytest_user_config = apathetic_testing.has_pytest_user_config
has_pytest_plugin_enabled = apathetic_testing.has_pytest_plugin_enabled
create_mock_superclass_test = apathetic_testing.create_mock_superclass_test
create_mock_version_info = apathetic_testing.create_mock_version_info
patch_everywhere = apathetic_testing.patch_everywhere

__all__ = [
    "LoggingIsolation",
    "LoggingLevelTesting",
    "LoggingTestLevel",
    "apathetic_testing",
    "atest_apathetic_logger",
    "atest_isolated_logging",
    "atest_logging_level_testing",
    "atest_logging_test_level",
    "atest_reset_logger_level",
    "create_mock_superclass_test",
    "create_mock_version_info",
    "detect_module_runtime_mode",
    "ensure_stitched_script_up_to_date",
    "ensure_zipapp_up_to_date",
    "has_pytest_plugin_enabled",
    "has_pytest_user_config",
    "is_running_under_pytest",
    "patch_everywhere",
    "runtime_swap",
]
