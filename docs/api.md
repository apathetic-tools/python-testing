---
layout: base
title: API Reference
permalink: /api/
---

# API Reference

Complete API documentation for Apathetic Python Testing.

## Quick Reference

| Category | Functions |
|----------|-----------|
| **File Loading** | [`load_jsonc()`](#load_jsonc), [`load_toml()`](#load_toml) |
| **Path Utilities** | [`normalize_path_string()`](#normalize_path_string), [`has_glob_chars()`](#has_glob_chars), [`get_glob_root()`](#get_glob_root), [`shorten_path()`](#shorten_path) |
| **Pattern Matching** | [`fnmatchcase_portable()`](#fnmatchcase_portable), [`is_excluded_raw()`](#is_excluded_raw) |
| **Module Detection** | [`detect_packages_from_files()`](#detect_packages_from_files), [`find_all_packages_under_path()`](#find_all_packages_under_path) |
| **System Detection** | [`is_ci()`](#is_ci), [`if_ci()`](#if_ci), [`is_running_under_pytest()`](#is_running_under_pytest), [`detect_runtime_mode()`](#detect_runtime_mode), [`capture_output()`](#capture_output), [`get_sys_version_info()`](#get_sys_version_info) |
| **Runtime Utilities** | [`find_python_command()`](#find_python_command), [`ensure_stitched_script_up_to_date()`](#ensure_stitched_script_up_to_date), [`ensure_zipapp_up_to_date()`](#ensure_zipapp_up_to_date), [`runtime_swap()`](#runtime_swap) |
| **Subprocess Utilities** | [`run_with_output()`](#run_with_output), [`run_with_separated_output()`](#run_with_separated_output) |
| **Text Processing** | [`plural()`](#plural), [`remove_path_in_error_message()`](#remove_path_in_error_message) |
| **Type Utilities** | [`safe_isinstance()`](#safe_isinstance), [`literal_to_set()`](#literal_to_set), [`cast_hint()`](#cast_hint), [`schema_from_typeddict()`](#schema_from_typeddict) |
| **Version Utilities** | [`create_version_info()`](#create_version_info) |
| **Testing Utilities** | [`detect_module_runtime_mode()`](#detect_module_runtime_mode), [`create_mock_superclass_test()`](#create_mock_superclass_test), [`patch_everywhere()`](#patch_everywhere) |
| **Constants** | [`CI_ENV_VARS`](#ci_env_vars) |

## File Loading

### load_jsonc

```python
load_jsonc(path: Path) -> dict[str, Any] | list[Any] | None
```

Load and parse a JSONC (JSON with Comments) file.

Supports:
- Single-line comments (`//` and `#`)
- Block comments (`/* */`)
- Trailing commas
- Empty files or files with only comments (returns `None`)

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `path` | `Path` | Path to the JSONC file |

**Returns:**
- `dict[str, Any] | list[Any]`: Parsed JSON data (dict or list)
- `None`: If the file is empty or contains only comments

**Raises:**
- `FileNotFoundError`: If the file doesn't exist
- `ValueError`: If the file is not a file, has invalid JSONC syntax, or has a scalar root

**Example:**
```python
from apathetic_testing import load_jsonc
from pathlib import Path

config = load_jsonc(Path("config.jsonc"))
# {
#   "name": "my_app",
#   "version": "1.0.0"
# }
```

### load_toml

```python
load_toml(path: Path, *, required: bool = False) -> dict[str, Any] | None
```

Load and parse a TOML file, supporting Python 3.10 and 3.11+.

Uses:
- `tomllib` (Python 3.11+ standard library)
- `tomli` (required for Python 3.10 - must be installed separately)

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `path` | `Path` | Path to the TOML file |
| `required` | `bool` | If `True`, raise `RuntimeError` when `tomli` is missing on Python 3.10. If `False`, return `None` when unavailable. Defaults to `False`. |

**Returns:**
- `dict[str, Any]`: Parsed TOML data as a dictionary
- `None`: If unavailable and `required=False`

**Raises:**
- `FileNotFoundError`: If the file doesn't exist
- `RuntimeError`: If `required=True` and neither `tomllib` nor `tomli` is available
- `ValueError`: If the file cannot be parsed

**Example:**
```python
from apathetic_testing import load_toml
from pathlib import Path

pyproject = load_toml(Path("pyproject.toml"), required=True)
```

## Path Utilities

### normalize_path_string

```python
normalize_path_string(raw: str) -> str
```

Normalize a user-supplied path string for cross-platform use.

Industry-standard (Git/Node/Python) rules:
- Treat both `/` and `\` as valid separators and normalize all to `/`
- Replace escaped spaces (`\ `) with real spaces
- Collapse redundant slashes (preserve protocol prefixes like `file://`)
- Never resolve `.` or `..` or touch the filesystem
- Never raise for syntax; normalization is always possible

This is purely lexical — it normalizes syntax, not filesystem state.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `raw` | `str` | Raw path string to normalize |

**Returns:**
- `str`: Normalized path string

**Example:**
```python
from apathetic_testing import normalize_path_string

path = normalize_path_string("src\\utils\\file.py")
# Returns: "src/utils/file.py"

path = normalize_path_string("src//utils///file.py")
# Returns: "src/utils/file.py"
```

### has_glob_chars

```python
has_glob_chars(s: str) -> bool
```

Check if a string contains glob pattern characters (`*`, `?`, `[`).

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `s` | `str` | String to check |

**Returns:**
- `bool`: `True` if the string contains glob characters, `False` otherwise

**Example:**
```python
from apathetic_testing import has_glob_chars

has_glob_chars("src/**/*.py")  # True
has_glob_chars("src/file.py")  # False
```

### get_glob_root

```python
get_glob_root(pattern: str) -> Path
```

Return the non-glob portion of a path pattern like `src/**/*.txt`.

Normalizes paths to cross-platform format.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `pattern` | `str` | Glob pattern string |

**Returns:**
- `Path`: The non-glob portion of the path

**Example:**
```python
from apathetic_testing import get_glob_root

root = get_glob_root("src/**/*.txt")
# Returns: Path("src")

root = get_glob_root("tests/unit/**/*.py")
# Returns: Path("tests/unit")
```

### shorten_path

```python
shorten_path(
    path: str | Path,
    bases: str | Path | list[str | Path]
) -> str
```

Return the shortest path relative to any base's common prefix.

Finds the longest shared prefix between `path` and each base path by comparing their path parts, and returns the shortest remaining portion of `path`. This works with any paths (files, directories, etc.) and does not require one path to be under the other.

When the common prefix is only root (`"/"`), returns the absolute path since a relative path from root is not useful.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `path` | `str \| Path` | Path to shorten |
| `bases` | `str \| Path \| list[str \| Path]` | Single base path or list of base paths to find common prefix with |

**Returns:**
- `str`: Shortest path relative to common prefix, or absolute path if common prefix is only root

**Examples:**
```python
from apathetic_testing import shorten_path

# Single base
result = shorten_path(
    "/home/user/code/serger/src/serger/logs.py",
    "/home/user/code/serger/tests/utils/patch_everywhere.py"
)
# Returns: "src/serger/logs.py"

# Multiple bases - returns shortest
result = shorten_path(
    "/home/user/code/serger/src/logs.py",
    ["/home/user/code/serger/tests/utils/patch.py",
     "/home/user/code/serger/src"]
)
# Returns: "logs.py" (shortest: common prefix with src/)

# Returns absolute path when only root in common
result = shorten_path(
    "/var/lib/file.py",
    ["/home/user", "/tmp"]
)
# Returns: "/var/lib/file.py" (absolute path)
```

## Pattern Matching

### fnmatchcase_portable

```python
fnmatchcase_portable(path: str, pattern: str) -> bool
```

Case-sensitive glob pattern matching with Python 3.10 `**` backport.

Uses `fnmatchcase` (case-sensitive) as the base, with backported support for recursive `**` patterns on Python 3.10.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `path` | `str` | The path to match against the pattern |
| `pattern` | `str` | The glob pattern to match |

**Returns:**
- `bool`: `True` if the path matches the pattern, `False` otherwise

**Example:**
```python
from apathetic_testing import fnmatchcase_portable

fnmatchcase_portable("src/utils/file.py", "src/**/*.py")  # True
fnmatchcase_portable("deep/nested/file.py", "**/*.py")    # True
fnmatchcase_portable("src/file.py", "src/*.py")            # True
```

### is_excluded_raw

```python
is_excluded_raw(
    path: Path | str,
    exclude_patterns: list[str],
    root: Path | str
) -> bool
```

Smart matcher for normalized inputs to check if a path matches exclusion patterns.

- Treats `path` as relative to `root` unless already absolute
- If `root` is a file, match directly
- Handles absolute or relative glob patterns
- Supports patterns with `../` to match files outside the exclude root
- Supports `**/` patterns for recursive matching

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `path` | `Path \| str` | Path to check against exclusion patterns |
| `exclude_patterns` | `list[str]` | List of glob patterns to exclude |
| `root` | `Path \| str` | Root directory for relative path resolution |

**Returns:**
- `bool`: `True` if the path matches any exclusion pattern, `False` otherwise

**Example:**
```python
from apathetic_testing import is_excluded_raw
from pathlib import Path

patterns = ["**/__pycache__/**", "*.pyc", "tests/**"]
root = Path(".")

is_excluded_raw("src/__pycache__/file.pyc", patterns, root)  # True
is_excluded_raw("src/utils/file.py", patterns, root)         # False
```

## Module Detection

### detect_packages_from_files

```python
detect_packages_from_files(
    file_paths: list[Path],
    package_name: str,
    *,
    source_bases: list[str] | None = None,
    _config_dir: Path | None = None
) -> tuple[set[str], list[str]]
```

Detect packages from file paths.

If files are under `source_bases` directories, treats everything after the matching base prefix as a package structure (regardless of `__init__.py`). Otherwise, follows Python's import rules: only detects regular packages (with `__init__.py` files). Falls back to configured `package_name` if none detected.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `file_paths` | `list[Path]` | List of file paths to check |
| `package_name` | `str` | Configured package name (used as fallback) |
| `source_bases` | `list[str] \| None` | Optional list of module base directories (absolute paths) |
| `_config_dir` | `Path \| None` | Optional config directory (unused, kept for compatibility) |

**Returns:**
- `tuple[set[str], list[str]]`: Tuple of (set of detected package names, list of parent directories). Package names always includes `package_name`. Parent directories are returned as absolute paths, deduplicated.

**Example:**
```python
from apathetic_testing import detect_packages_from_files
from pathlib import Path

files = [Path("src/mypkg/module.py"), Path("src/otherpkg/file.py")]
packages, parents = detect_packages_from_files(
    files,
    "mypkg",
    source_bases=["/path/to/src"]
)
# packages: {"mypkg", "otherpkg", "mypkg"} (includes configured name)
# parents: ["/path/to/src"]
```

### find_all_packages_under_path

```python
find_all_packages_under_path(root_path: Path) -> set[str]
```

Find all package names under a directory by scanning for `__init__.py` files.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `root_path` | `Path` | Path to the root directory to scan |

**Returns:**
- `set[str]`: Set of package names found under the root directory

**Example:**
```python
from apathetic_testing import find_all_packages_under_path
from pathlib import Path

packages = find_all_packages_under_path(Path("src"))
# Returns: {"mypkg", "otherpkg"} (all top-level packages with __init__.py)
```

## System Detection

### is_ci

```python
is_ci() -> bool
```

Check if running in a CI environment.

Returns `True` if any of the following environment variables are set:
- `CI`: Generic CI indicator (set by most CI systems)
- `GITHUB_ACTIONS`: GitHub Actions specific
- `GIT_TAG`: Indicates a tagged build
- `GITHUB_REF`: GitHub Actions ref (branch/tag)

**Returns:**
- `bool`: `True` if running in CI, `False` otherwise

**Example:**
```python
from apathetic_testing import is_ci

if is_ci():
    print("Running in CI environment")
    # Adjust behavior for CI
```

### if_ci

```python
if_ci(ci_value: T, local_value: T) -> T
```

Return different values based on CI environment.

Useful for tests that need different behavior or expectations in CI vs local development environments.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `ci_value` | `T` | Value to return when running in CI |
| `local_value` | `T` | Value to return when running locally |

**Returns:**
- `T`: `ci_value` if running in CI, otherwise `local_value`

**Example:**
```python
from apathetic_testing import if_ci

# Different regex patterns for commit hashes
commit_pattern = if_ci(
    r"[0-9a-f]{4,}",  # CI: expect actual commit hash
    r"unknown \\(local build\\)"  # Local: expect placeholder
)
```

### is_running_under_pytest

```python
is_running_under_pytest() -> bool
```

Detect if code is running under pytest.

Checks multiple indicators:
- Environment variables set by pytest
- Command-line arguments containing 'pytest'

**Returns:**
- `bool`: `True` if running under pytest, `False` otherwise

**Example:**
```python
from apathetic_testing import is_running_under_pytest

if is_running_under_pytest():
    # Use test-specific configuration
    pass
```

### detect_runtime_mode

```python
detect_runtime_mode(package_name: str) -> str
```

Detect how the package is being executed.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `package_name` | `str` | Name of the package to check |

**Returns:**
- `str`: Runtime mode, one of:
  - `"package"`: Package installed via pip/poetry
  - `"stitched"`: Single-file stitched script
  - `"zipapp"`: Python zipapp (`.pyz` file)
  - `"frozen"`: Frozen executable (PyInstaller, etc.)

**Example:**
```python
from apathetic_testing import detect_runtime_mode

mode = detect_runtime_mode("my_package")
print(f"Running in {mode} mode")
```

### capture_output

```python
capture_output() -> ContextManager[CapturedOutput]
```

Temporarily capture stdout and stderr.

Any exception raised inside the block is re-raised with the captured output attached as `exc.captured_output`.

**Returns:**
- `ContextManager[CapturedOutput]`: Context manager that yields a `CapturedOutput` object

**CapturedOutput Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `stdout` | `StringIO` | Captured stdout |
| `stderr` | `StringIO` | Captured stderr |
| `merged` | `StringIO` | Merged stdout and stderr |

**CapturedOutput Methods:**

| Method | Description |
|--------|-------------|
| `as_dict() -> dict[str, str]` | Return contents as plain strings for serialization |

**Example:**
```python
from apathetic_testing import capture_output
import sys

with capture_output() as cap:
    print("Hello, world!")
    print("Error message", file=sys.stderr)

print(f"stdout: {cap.stdout.getvalue()}")
print(f"stderr: {cap.stderr.getvalue()}")
print(f"merged: {cap.merged.getvalue()}")

# Or convert to dict
output = cap.as_dict()
```

### get_sys_version_info

```python
get_sys_version_info() -> tuple[int, int, int] | tuple[int, int, int, str, int]
```

Get Python version information.

Wrapper for `sys.version_info`.

**Returns:**
- `tuple[int, int, int]`: Version tuple `(major, minor, micro)`
- `tuple[int, int, int, str, int]`: Version tuple with releaselevel and serial (for release candidates)

**Example:**
```python
from apathetic_testing import get_sys_version_info

version = get_sys_version_info()
print(f"Python {version[0]}.{version[1]}.{version[2]}")
```

## Runtime Utilities

### ensure_stitched_script_up_to_date

```python
ensure_stitched_script_up_to_date(
    *,
    root: Path,
    script_name: str | None = None,
    package_name: str,
    command_path: str | None = None,
    log_level: str | None = None
) -> Path
```

Rebuild stitched script if missing or outdated.

Checks if the stitched script exists and is newer than all source files. If not, rebuilds it using either the provided bundler script or the Poetry-installed `serger` module.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `root` | `Path` | Project root directory |
| `script_name` | `str \| None` | Optional name of the stitched script (without .py extension). If None, defaults to `package_name`. |
| `package_name` | `str` | Name of the package (e.g., "apathetic_testing") |
| `bundler_script` | `str \| None` | Optional path to bundler script (relative to root). If provided and exists, uses `python {bundler_script}`. Otherwise, uses `python -m serger --config .serger.jsonc`. |
| `log_level` | `str \| None` | Optional log level to pass to serger. If provided, adds `--log-level=<log_level>` to the serger command. |

**Returns:**
- `Path`: Path to the stitched script

**Raises:**
- `RuntimeError`: If the script generation fails

**Example:**
```python
from apathetic_testing import ensure_stitched_script_up_to_date
from pathlib import Path

# Using package_name as script_name (default)
script_path = ensure_stitched_script_up_to_date(
    root=Path("."),
    package_name="my_package"
)

# Using a custom script name
script_path = ensure_stitched_script_up_to_date(
    root=Path("."),
    script_name="my_script",
    package_name="my_package"
)

# Using a local bundler script
script_path = ensure_stitched_script_up_to_date(
    root=Path("."),
    script_name="my_script",
    package_name="my_package",
    command_path="bin/serger.py"
)

# Using a custom log level
script_path = ensure_stitched_script_up_to_date(
    root=Path("."),
    package_name="my_package",
    log_level="debug"
)
```

### ensure_zipapp_up_to_date

```python
ensure_zipapp_up_to_date(
    *,
    root: Path,
    script_name: str | None = None,
    package_name: str,
    command_path: str | None = None,
    log_level: str | None = None
) -> Path
```

Rebuild zipapp if missing or outdated.

Checks if the zipapp exists and is newer than all source files. If not, rebuilds it using zipbundler.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `root` | `Path` | Project root directory |
| `script_name` | `str \| None` | Optional name of the zipapp (without .pyz extension). If None, defaults to `package_name`. |
| `package_name` | `str` | Name of the package (e.g., "apathetic_testing") |
| `command_path` | `str \| None` | Optional path to bundler script (relative to root). If provided and exists, uses `python {command_path}`. Otherwise, uses zipbundler. |
| `log_level` | `str \| None` | Optional log level to pass to zipbundler. If provided, adds `--log-level=<log_level>` to the zipbundler command. |

**Returns:**
- `Path`: Path to the zipapp

**Raises:**
- `RuntimeError`: If the zipapp generation fails

**Example:**
```python
from apathetic_testing import ensure_zipapp_up_to_date
from pathlib import Path

# Using package_name as script_name (default)
zipapp_path = ensure_zipapp_up_to_date(
    root=Path("."),
    package_name="my_package"
)

# Using a custom script name
zipapp_path = ensure_zipapp_up_to_date(
    root=Path("."),
    script_name="my_script",
    package_name="my_package"
)

# Using a custom log level
zipapp_path = ensure_zipapp_up_to_date(
    root=Path("."),
    package_name="my_package",
    log_level="debug"
)

# Using a local bundler script
zipapp_path = ensure_zipapp_up_to_date(
    root=Path("."),
    package_name="my_package",
    command_path="bin/zipapp_builder.py"
)
```

### runtime_swap

```python
runtime_swap(
    *,
    root: Path,
    package_name: str,
    script_name: str | None = None,
    stitch_command: str | None = None,
    zipapp_command: str | None = None,
    mode: str | None = None,
    log_level: str | None = None
) -> bool
```

Pre-import hook — runs before any tests or plugins are imported.

Swaps in the appropriate runtime module based on `RUNTIME_MODE`:
- `package` (default): uses `src/{package_name}` (no swap needed)
- `stitched`: uses `dist/{script_name}.py` (serger-built single file)
- `zipapp`: uses `dist/{script_name}.pyz` (zipbundler-built zipapp)

This ensures all test imports work transparently regardless of runtime mode.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `root` | `Path` | Project root directory |
| `package_name` | `str` | Name of the package (e.g., "apathetic_testing") |
| `script_name` | `str \| None` | Optional name of the stitched script (without extension). If None, defaults to `package_name`. |
| `stitch_command` | `str \| None` | Optional path to bundler script for stitched mode (relative to root). If provided and exists, uses `python {stitch_command}`. Otherwise, uses `python -m serger --config .serger.jsonc`. |
| `zipapp_command` | `str \| None` | Optional path to bundler script for zipapp mode (relative to root). If provided and exists, uses `python {zipapp_command}`. Otherwise, uses zipbundler. |
| `mode` | `str \| None` | Runtime mode override. If None, reads from `RUNTIME_MODE` env var. |
| `log_level` | `str \| None` | Optional log level to pass to serger and zipbundler. If provided, adds `--log-level=<log_level>` to their commands. |

**Returns:**
- `bool`: `True` if swap was performed, `False` if in package mode

**Raises:**
- `pytest.UsageError`: If mode is invalid or build fails

**Example:**
```python
from apathetic_testing import runtime_swap
from pathlib import Path

# In pytest conftest.py or similar
# Using package_name as script_name (default), Poetry-installed serger
runtime_swap(
    root=Path(__file__).parent.parent,
    package_name="my_package",
    mode="stitched"  # or None to read from RUNTIME_MODE env var
)

# Using a custom script name
runtime_swap(
    root=Path(__file__).parent.parent,
    package_name="my_package",
    script_name="my_script",
    mode="stitched"
)

# Using a local bundler script for stitched mode
runtime_swap(
    root=Path(__file__).parent.parent,
    package_name="my_package",
    script_name="my_script",
    stitch_command="bin/serger.py",
    mode="stitched"
)

# Using a local bundler script for zipapp mode
runtime_swap(
    root=Path(__file__).parent.parent,
    package_name="my_package",
    script_name="my_script",
    zipapp_command="bin/zipapp_builder.py",
    mode="zipapp"
)

# Using a custom log level
runtime_swap(
    root=Path(__file__).parent.parent,
    package_name="my_package",
    mode="stitched",
    log_level="debug"
)
```

## Subprocess Utilities

### run_with_output

```python
run_with_output(
    args: list[str],
    *,
    cwd: Path | str | None = None,
    initial_env: dict[str, str] | None = None,
    env: dict[str, str] | None = None,
    forward_to: str | None = "normal",
    check: bool = False,
    **kwargs: Any
) -> SubprocessResult
```

Run subprocess and capture all output with optional forwarding.

This helper captures subprocess output and can optionally forward it to different destinations. It ensures captured output is available for error messages and can be displayed in real-time if desired.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `args` | `list[str]` | Command and arguments to run |
| `cwd` | `Path \| str \| None` | Working directory |
| `initial_env` | `dict[str, str] \| None` | Initial environment state. If None, uses `os.environ.copy()`. If provided, starts with this environment (can be empty dict for blank environment). |
| `env` | `dict[str, str] \| None` | Additional environment variables to add/override |
| `forward_to` | `str \| None` | Where to forward captured output. Options: `"bypass"` (forward to `sys.__stdout__`/`sys.__stderr__`), `"normal"` (forward to `sys.stdout`/`sys.stderr`), `None` (don't forward). Defaults to `"normal"`. |
| `check` | `bool` | If True, raise `CalledProcessError` on non-zero exit |
| `**kwargs` | `Any` | Additional arguments passed to `subprocess.run()` |

**Returns:**
- `SubprocessResult`: Result object with all captured output

**SubprocessResult Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `stdout` | `str` | Captured stdout |
| `stderr` | `str` | Captured stderr |
| `returncode` | `int` | Return code from subprocess |
| `all_output` | `str` | All output combined: stdout + stderr |

**Example:**
```python
from apathetic_testing import run_with_output
import sys

# Use current environment with additional vars
result = run_with_output(
    [sys.executable, "-m", "serger", "--config", "config.json"],
    cwd=tmp_path,
    env={"LOG_LEVEL": "test"},
)

# Forward output to bypass (visible in real-time, bypasses capsys)
result = run_with_output(
    [sys.executable, "-m", "serger", "--config", "config.json"],
    cwd=tmp_path,
    env={"LOG_LEVEL": "test"},
    forward_to="bypass",
)

# On test failure, output will be included
assert result.returncode == 0, f"Failed: {result.all_output}"
```

### run_with_separated_output

```python
run_with_separated_output(
    args: list[str],
    *,
    cwd: Path | str | None = None,
    initial_env: dict[str, str] | None = None,
    env: dict[str, str] | None = None,
    check: bool = False,
    **kwargs: Any
) -> SubprocessResultWithBypass
```

Run subprocess with stdout and `__stdout__` captured separately.

This uses a Python wrapper to modify `sys.__stdout__` before the command runs, allowing code to write to stdout and `__stdout__` normally without any changes. Normal output (stdout) is captured, while bypass output (`__stdout__`) goes to the parent's stdout.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `args` | `list[str]` | Command and arguments to run (must be a Python command) |
| `cwd` | `Path \| str \| None` | Working directory |
| `initial_env` | `dict[str, str] \| None` | Initial environment state. If None, uses `os.environ.copy()`. If provided, starts with this environment (can be empty dict for blank environment). |
| `env` | `dict[str, str] \| None` | Additional environment variables to add/override |
| `check` | `bool` | If True, raise `CalledProcessError` on non-zero exit |
| `**kwargs` | `Any` | Additional arguments passed to `subprocess.run()` |

**Returns:**
- `SubprocessResultWithBypass`: Result object with separate stdout and bypass_output

**SubprocessResultWithBypass Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `stdout` | `str` | Captured stdout (normal output, excluding bypass) |
| `stderr` | `str` | Captured stderr |
| `bypass_output` | `str` | Bypass output (written to `sys.__stdout__`) |
| `returncode` | `int` | Return code from subprocess |
| `all_output` | `str` | All output combined: stdout + stderr + bypass |

**Example:**
```python
from apathetic_testing import run_with_separated_output
import sys

result = run_with_separated_output(
    [sys.executable, "-m", "serger", "--config", "config.json"],
    cwd=tmp_path,
    env={"LOG_LEVEL": "test"},
)
# stdout contains normal output (captured)
# bypass_output contains output written to __stdout__
assert result.returncode == 0, f"Failed: {result.all_output}"
```

## Text Processing

### plural

```python
plural(obj: Any) -> str
```

Return `'s'` if `obj` represents a plural count.

Accepts ints, floats, and any object implementing `__len__()`. Returns `''` for singular or zero.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `obj` | `Any` | Object to check (int, float, or object with `__len__()`) |

**Returns:**
- `str`: `'s'` for plural, `''` for singular or zero

**Example:**
```python
from apathetic_testing import plural

count = 5
print(f"{count} file{plural(count)}")  # "5 files"

count = 1
print(f"{count} file{plural(count)}")  # "1 file"

items = [1, 2, 3]
print(f"{len(items)} item{plural(items)}")  # "3 items"
```

### remove_path_in_error_message

```python
remove_path_in_error_message(inner_msg: str, path: Path) -> str
```

Remove redundant file path mentions (and nearby filler) from error messages.

Useful when wrapping a lower-level exception that already embeds its own file reference, so the higher-level message can use its own path without duplication.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `inner_msg` | `str` | Error message that may contain path references |
| `path` | `Path` | Path to remove from the message |

**Returns:**
- `str`: Error message with path references removed

**Example:**
```python
from apathetic_testing import remove_path_in_error_message
from pathlib import Path

error_msg = "Invalid JSONC syntax in /path/to/config.jsonc: Expecting value"
path = Path("/path/to/config.jsonc")

clean_msg = remove_path_in_error_message(error_msg, path)
# Returns: "Invalid JSONC syntax: Expecting value"
```

## Type Utilities

### safe_isinstance

```python
safe_isinstance(value: Any, expected_type: Any) -> bool
```

Like `isinstance()`, but safe for TypedDicts and typing generics.

Handles:
- `typing.Union`, `Optional`, `Any`
- `typing.NotRequired`
- TypedDict subclasses
- `list[...]` with inner types
- `dict[...]` with key/value types
- `tuple[...]` with element types
- Defensive fallback for exotic typing constructs

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `value` | `Any` | Value to check |
| `expected_type` | `Any` | Type to check against |

**Returns:**
- `bool`: `True` if value matches the expected type, `False` otherwise

**Example:**
```python
from apathetic_testing import safe_isinstance
from typing import TypedDict, Optional

class Config(TypedDict):
    name: str
    value: int

data = {"name": "test", "value": 42}

# Works with TypedDict
safe_isinstance(data, Config)  # True

# Works with generics
safe_isinstance([1, 2, 3], list[int])  # True
safe_isinstance({"a": 1, "b": 2}, dict[str, int])  # True

# Works with Optional
safe_isinstance(None, Optional[str])  # True
safe_isinstance("test", Optional[str])  # True
```

### literal_to_set

```python
literal_to_set(literal_type: Any) -> set[Any]
```

Extract values from a `Literal` type as a set.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `literal_type` | `Any` | A `Literal` type (e.g., `Literal["a", "b"]`) |

**Returns:**
- `set[Any]`: A set containing all values from the `Literal` type

**Raises:**
- `TypeError`: If the input is not a `Literal` type

**Example:**
```python
from apathetic_testing import literal_to_set
from typing import Literal

Mode = Literal["dev", "prod", "test"]
valid_modes = literal_to_set(Mode)
# Returns: {"dev", "prod", "test"}

if "dev" in valid_modes:
    print("Valid mode")
```

### cast_hint

```python
cast_hint(typ: type[T], value: Any) -> T
```

Explicit cast that documents intent but is purely for type hinting.

A drop-in replacement for `typing.cast`, meant for places where:
- You want to silence mypy's redundant-cast warnings
- You want to signal "this narrowing is intentional"
- You need IDEs (like Pylance) to retain strong inference on a value

Does not handle `Union`, `Optional`, or nested generics: stick to `cast()` for those, because unions almost always represent a meaningful type narrowing.

This function performs **no runtime checks**.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `typ` | `type[T]` | Target type |
| `value` | `Any` | Value to cast |

**Returns:**
- `T`: The value (unchanged at runtime)

**Example:**
```python
from apathetic_testing import cast_hint

# Type narrowing for type checkers
value: Any = get_data()
typed_value = cast_hint(dict[str, int], value)
# typed_value is now inferred as dict[str, int]
```

### schema_from_typeddict

```python
schema_from_typeddict(td: type[Any]) -> dict[str, Any]
```

Extract field names and their annotated types from a TypedDict.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `td` | `type[Any]` | TypedDict class |

**Returns:**
- `dict[str, Any]`: Dictionary mapping field names to their types

**Example:**
```python
from apathetic_testing import schema_from_typeddict
from typing import TypedDict

class Config(TypedDict):
    name: str
    value: int

schema = schema_from_typeddict(Config)
# Returns: {"name": str, "value": int}
```

## Version Utilities

### create_version_info

```python
create_version_info(major: int, minor: int, micro: int = 0) -> Any
```

Create a mock `sys.version_info` object with major and minor attributes.

This properly mocks `sys.version_info` so it can be used with attribute access (`.major`, `.minor`) and tuple comparison, matching the behavior of the real `sys.version_info` object (which is a named tuple).

Useful for testing or when you need to simulate different Python versions.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `major` | `int` | Major version number (e.g., 3) |
| `minor` | `int` | Minor version number (e.g., 11) |
| `micro` | `int` | Micro version number (default: 0) |

**Returns:**
- `Any`: A mock version_info object with `.major`, `.minor`, `.micro` attributes and tuple-like comparison support

**Example:**
```python
from apathetic_testing import create_version_info

version = create_version_info(3, 11)
assert version.major == 3
assert version.minor == 11
assert version >= (3, 10)
```

## Testing Utilities

### detect_module_runtime_mode

```python
detect_module_runtime_mode(
    mod: ModuleType,
    *,
    stitch_hints: set[str] | None = None
) -> str
```

Detect the runtime mode of a specific module.

Determines whether a module was built as part of a stitched single-file script, zipapp archive, or standard package by checking for markers and file path attributes.

This check prioritizes marker-based detection (`__STITCHED__` and `__STANDALONE__` attributes) as the most reliable method, but falls back to path heuristics when markers are not present.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `mod` | `ModuleType` | Module to check |
| `stitch_hints` | `set[str] \| None` | Set of path hints to identify stitched modules. Defaults to `{"/dist/", "stitched"}`. Used as fallback when markers are not present. |

**Returns:**
- `str`: One of:
  - `"stitched"` if module has `__STITCHED__` or `__STANDALONE__` marker, or if `__file__` path matches stitch_hints
  - `"zipapp"` if module `__file__` indicates zipapp (contains `.pyz`)
  - `"package"` for regular package modules

**Raises:**
- `TypeError`: If mod is not a ModuleType

**Example:**
```python
from apathetic_testing import detect_module_runtime_mode
import apathetic_testing

# Detect module runtime mode
mode = detect_module_runtime_mode(apathetic_testing)
print(f"apathetic_testing is running in {mode} mode")

# With custom stitch hints
mode = detect_module_runtime_mode(
    apathetic_testing,
    stitch_hints={"/dist/", "bundled", "embedded"}
)
```

### create_mock_superclass_test

```python
create_mock_superclass_test(
    mixin_class: type,
    parent_class: type,
    method_name: str,
    camel_case_method_name: str,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch
) -> None
```

Test that a mixin's snake_case method calls parent's camelCase via `super()`.

Creates a test class with controlled MRO:
- TestClass inherits from mixin_class, then MockBaseClass
- MockBaseClass provides the camelCase method that `super()` resolves to
- Mocks the camelCase method and verifies it's called

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `mixin_class` | `type` | The mixin class containing the snake_case method |
| `parent_class` | `type` | The parent class with the camelCase method (e.g., `logging.Logger`) |
| `method_name` | `str` | Name of the snake_case method to test (e.g., "add_filter") |
| `camel_case_method_name` | `str` | Name of the camelCase method to mock (e.g., "addFilter") |
| `args` | `tuple[Any, ...]` | Arguments to pass to the snake_case method |
| `kwargs` | `dict[str, Any]` | Keyword arguments to pass to the snake_case method |
| `monkeypatch` | `pytest.MonkeyPatch` | pytest.MonkeyPatch fixture for patching |

**Raises:**
- `AssertionError`: If the camelCase method was not called as expected

**Example:**
```python
from apathetic_testing import create_mock_superclass_test
import logging
import pytest

def test_mixin_calls_parent(monkeypatch):
    create_mock_superclass_test(
        MyMixin,
        logging.Logger,
        "add_filter",
        "addFilter",
        (logging.Filter(),),
        {},
        monkeypatch
    )
```

### patch_everywhere

```python
patch_everywhere(
    mp: pytest.MonkeyPatch,
    mod_env: ModuleType | Any,
    func_name: str,
    replacement_func: Callable[..., object],
    *,
    package_prefix: str | Sequence[str],
    stitch_hints: set[str] | None = None,
    create_if_missing: bool = False,
    caller_func_name: str | None = None
) -> None
```

Replace a function everywhere it was imported.

Works in both package and stitched single-file runtimes. Walks `sys.modules` once and handles:
- the defining module
- any other module that imported the same function object
- any freshly reloaded stitched modules (heuristic: path matches hints)

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `mp` | `pytest.MonkeyPatch` | pytest.MonkeyPatch instance to use for patching |
| `mod_env` | `ModuleType \| Any` | Module or object containing the function to patch |
| `func_name` | `str` | Name of the function to patch |
| `replacement_func` | `Callable[..., object]` | Function to replace the original with |
| `package_prefix` | `str \| Sequence[str]` | Package name prefix(es) to filter modules. Can be a single string (e.g., "apathetic_testing") or a sequence of strings (e.g., ["apathetic_testing", "my_package"]) to patch across multiple packages. |
| `stitch_hints` | `set[str] \| None` | Set of path hints to identify stitched modules. Defaults to `{"/dist/", "stitched"}`. When providing custom hints, you must be certain of the path attributes of your stitched file, as this uses substring matching on the module's `__file__` path. This is a heuristic fallback when identity checks fail (e.g., when modules are reloaded). |
| `create_if_missing` | `bool` | If True, create the attribute if it doesn't exist. If False (default), raise TypeError if the function doesn't exist. |
| `caller_func_name` | `str \| None` | If provided, only patch `__globals__` for this specific function to handle direct calls. If None (default), patch `__globals__` for all functions in stitched modules that reference the original function. |

**Raises:**
- `TypeError`: If the function doesn't exist and `create_if_missing=False`

**Example:**
```python
from apathetic_testing import patch_everywhere
import pytest
import my_module

def test_patch_function(monkeypatch):
    def mock_func():
        return "mocked"
    
    patch_everywhere(
        monkeypatch,
        my_module,
        "original_func",
        mock_func,
        package_prefix="my_module"
    )
```

## Constants

### CI_ENV_VARS

```python
CI_ENV_VARS: tuple[str, ...]
```

Tuple of CI environment variable names that indicate a CI environment.

Default values:
- `"CI"`
- `"GITHUB_ACTIONS"`
- `"GIT_TAG"`
- `"GITHUB_REF"`

**Example:**
```python
from apathetic_testing import CI_ENV_VARS

print(CI_ENV_VARS)  # ("CI", "GITHUB_ACTIONS", "GIT_TAG", "GITHUB_REF")
```

## Namespace Class

All utilities are also available through the `apathetic_testing` namespace class:

```python
from apathetic_testing import apathetic_testing

# Use via namespace
config = apathetic_testing.load_jsonc(Path("config.jsonc"))
is_ci = apathetic_testing.is_ci()
mode = apathetic_testing.detect_runtime_mode("my_package")
```

This is useful when embedding the library as a single-file script to minimize global namespace pollution.
