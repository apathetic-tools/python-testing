---
layout: base
title: Examples
permalink: /examples/
---

# Usage Examples

Advanced usage patterns and examples for Apathetic Python Testing.

## Configuration File Loading

### Loading JSONC Configuration

```python
from apathetic_testing import load_jsonc
from pathlib import Path

# Load a configuration file with comments
config = load_jsonc(Path("config.jsonc"))

if config:
    app_name = config.get("name", "default")
    version = config.get("version", "1.0.0")
    print(f"{app_name} v{version}")
```

### Loading TOML Configuration

```python
from apathetic_testing import load_toml
from pathlib import Path

# Load pyproject.toml
pyproject = load_toml(Path("pyproject.toml"), required=True)

if pyproject:
    project_name = pyproject.get("project", {}).get("name", "unknown")
    print(f"Project: {project_name}")
```

### Handling Missing Files

```python
from apathetic_testing import load_jsonc, load_toml
from pathlib import Path

# Try to load config, handle gracefully if missing
config = load_jsonc(Path("config.jsonc"))
if config is None:
    print("No configuration found, using defaults")
    config = {"name": "default", "version": "1.0.0"}

# For TOML, use required=False to return None instead of raising
pyproject = load_toml(Path("pyproject.toml"), required=False)
if pyproject is None:
    print("pyproject.toml not available (Python 3.10 without tomli)")
```

## Path Normalization and Glob Patterns

### Cross-Platform Path Handling

```python
from apathetic_testing import normalize_path_string, has_glob_chars, get_glob_root
from pathlib import Path

# Normalize Windows paths
windows_path = "src\\utils\\file.py"
normalized = normalize_path_string(windows_path)
print(normalized)  # "src/utils/file.py"

# Handle escaped spaces
path_with_spaces = "my\\ project\\ file.py"
normalized = normalize_path_string(path_with_spaces)
print(normalized)  # "my project file.py"

# Check for glob patterns
pattern = "src/**/*.py"
if has_glob_chars(pattern):
    root = get_glob_root(pattern)
    print(f"Glob root: {root}")  # Path("src")
```

## Pattern Matching and Exclusion

### Recursive Glob Matching

```python
from apathetic_testing import fnmatchcase_portable

# Match files recursively
files = [
    "src/main.py",
    "src/utils/helper.py",
    "src/utils/nested/deep.py",
    "tests/test_main.py",
]

pattern = "src/**/*.py"
matched = [f for f in files if fnmatchcase_portable(f, pattern)]
# Returns: ["src/main.py", "src/utils/helper.py", "src/utils/nested/deep.py"]
```

### Exclusion Pattern Checking

```python
from apathetic_testing import is_excluded_raw
from pathlib import Path

# Define exclusion patterns
exclude_patterns = [
    "**/__pycache__/**",
    "*.pyc",
    "*.pyo",
    "tests/**",
    ".git/**",
]

root = Path(".")

# Check if files should be excluded
files_to_check = [
    "src/utils/file.py",
    "src/__pycache__/file.pyc",
    "tests/test_file.py",
    ".git/config",
]

for file_path in files_to_check:
    if is_excluded_raw(file_path, exclude_patterns, root):
        print(f"{file_path} is excluded")
    else:
        print(f"{file_path} is included")
```

### Advanced Exclusion with Relative Paths

```python
from apathetic_testing import is_excluded_raw
from pathlib import Path

# Patterns with ../ to match files outside the root
exclude_patterns = [
    "../docs/**",  # Exclude docs directory outside project
    "**/node_modules/**",
]

root = Path("project")
file_path = Path("../docs/README.md")

if is_excluded_raw(file_path, exclude_patterns, root):
    print("File is excluded")
```

## System Detection

### CI Environment Detection

```python
from apathetic_testing import is_ci

def setup_environment():
    if is_ci():
        print("Running in CI environment")
        # Use CI-specific settings
        log_level = "warning"
        enable_debug = False
    else:
        print("Running locally")
        # Use development settings
        log_level = "debug"
        enable_debug = True
    
    return log_level, enable_debug
```

### Runtime Mode Detection

```python
from apathetic_testing import detect_runtime_mode

def get_build_info():
    mode = detect_runtime_mode("my_package")
    
    if mode == "package":
        print("Running as package")
    elif mode == "stitched":
        print("Running as stitched script")
    elif mode == "zipapp":
        print("Running as zipapp")
    elif mode == "frozen":
        print("Running as frozen executable")
    
    return mode
```

### Pytest Detection

```python
from apathetic_testing import is_running_under_pytest

def get_config():
    if is_running_under_pytest():
        # Use test configuration
        return {
            "database": "test.db",
            "log_level": "error",
        }
    else:
        # Use production configuration
        return {
            "database": "prod.db",
            "log_level": "info",
        }
```

## Output Capture

### Capturing CLI Output

```python
from apathetic_testing import capture_output
import sys

def run_command():
    with capture_output() as cap:
        print("Processing files...")
        print("File 1 processed", file=sys.stderr)
        print("File 2 processed")
        print("Complete!", file=sys.stderr)
    
    # Access captured output
    stdout = cap.stdout.getvalue()
    stderr = cap.stderr.getvalue()
    merged = cap.merged.getvalue()
    
    return {
        "stdout": stdout,
        "stderr": stderr,
        "merged": merged,
    }
```

### Capturing with Exception Handling

```python
from apathetic_testing import capture_output
import sys

def safe_command():
    try:
        with capture_output() as cap:
            # Some operation that might fail
            print("Starting operation")
            raise ValueError("Something went wrong")
    except ValueError as e:
        # Captured output is attached to the exception
        if hasattr(e, "captured_output"):
            print(f"Error occurred. Output: {e.captured_output.merged.getvalue()}")
        raise
```

### Converting to Dictionary

```python
from apathetic_testing import capture_output
import sys

with capture_output() as cap:
    print("Output line 1")
    print("Output line 2", file=sys.stderr)

# Convert to dictionary for serialization
output_dict = cap.as_dict()
# {
#     "stdout": "Output line 1\n",
#     "stderr": "Output line 2\n",
#     "merged": "Output line 1\nOutput line 2\n"
# }
```

## Text Processing

### Pluralization

```python
from apathetic_testing import plural

def format_count(items):
    count = len(items)
    return f"{count} item{plural(items)}"

print(format_count([1, 2, 3]))  # "3 items"
print(format_count([1]))         # "1 item"
print(format_count([]))          # "0 items"

# Works with numbers too
print(f"5 file{plural(5)}")      # "5 files"
print(f"1 file{plural(1)}")      # "1 file"
```

### Error Message Cleanup

```python
from apathetic_testing import remove_path_in_error_message, load_jsonc
from pathlib import Path

def load_config_safely(path: Path):
    try:
        return load_jsonc(path)
    except ValueError as e:
        # Remove redundant path from error message
        clean_msg = remove_path_in_error_message(str(e), path)
        raise ValueError(f"Failed to load config: {clean_msg}") from e

# Usage
try:
    config = load_config_safely(Path("config.jsonc"))
except ValueError as e:
    print(e)  # "Failed to load config: Invalid JSONC syntax: Expecting value"
```

## Type Utilities

### Safe Type Checking

```python
from apathetic_testing import safe_isinstance
from typing import TypedDict, Optional, Literal

class Config(TypedDict):
    name: str
    value: int
    optional_field: Optional[str]

# Check TypedDict
data = {"name": "test", "value": 42}
if safe_isinstance(data, Config):
    print("Valid config")

# Check generics
items = [1, 2, 3]
if safe_isinstance(items, list[int]):
    print("List of integers")

# Check Optional
value: Optional[str] = None
if safe_isinstance(value, Optional[str]):
    print("Valid optional value")
```

### Literal Type Validation

```python
from apathetic_testing import literal_to_set
from typing import Literal

Mode = Literal["dev", "prod", "test"]

def validate_mode(mode: str) -> bool:
    valid_modes = literal_to_set(Mode)
    return mode in valid_modes

# Usage
if validate_mode("dev"):
    print("Valid mode")
else:
    print("Invalid mode")
```

### TypedDict Schema Extraction

```python
from apathetic_testing import schema_from_typeddict
from typing import TypedDict

class UserConfig(TypedDict):
    username: str
    email: str
    age: int

# Extract schema
schema = schema_from_typeddict(UserConfig)
# Returns: {"username": str, "email": str, "age": int}

# Use for validation or documentation
for field, field_type in schema.items():
    print(f"{field}: {field_type}")
```

## Complete CLI Application Example

A complete example combining multiple utilities:

```python
#!/usr/bin/env python3
"""Example CLI application using Apathetic Python Testing."""

import sys
from pathlib import Path
from apathetic_testing import (
    load_jsonc,
    load_toml,
    is_ci,
    detect_runtime_mode,
    capture_output,
    plural,
    normalize_path_string,
)

def main():
    # Detect environment
    if is_ci():
        print("Running in CI environment")
    
    mode = detect_runtime_mode("my_app")
    print(f"Runtime mode: {mode}")
    
    # Load configuration
    config_path = Path("config.jsonc")
    if config_path.exists():
        config = load_jsonc(config_path)
        if config:
            print(f"Loaded config: {config.get('name', 'unknown')}")
    
    # Process files
    files = ["file1.py", "file2.py", "file3.py"]
    print(f"Processing {len(files)} file{plural(files)}...")
    
    # Capture output from processing
    with capture_output() as cap:
        for file in files:
            normalized = normalize_path_string(file)
            print(f"Processing {normalized}")
    
    print(f"Output:\n{cap.merged.getvalue()}")

if __name__ == "__main__":
    main()
```

## Integration with Build Tools

### Using with serger

```python
from apathetic_testing import detect_runtime_mode, load_jsonc
from pathlib import Path

def get_build_config():
    mode = detect_runtime_mode("my_package")
    
    if mode == "stitched":
        # Load stitched-specific config
        config = load_jsonc(Path(".serger.jsonc"))
        return config.get("stitched", {})
    else:
        # Use package config
        return {}
```

## Next Steps

- **[API Reference]({{ '/api' | relative_url }})** — Complete API documentation
- **[Quick Start Guide]({{ '/quickstart' | relative_url }})** — Get up and running quickly
- **[Contributing]({{ '/contributing' | relative_url }})** — Learn how to contribute
