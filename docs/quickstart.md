---
layout: base
title: Quick Start
permalink: /quickstart/
---

# Quick Start Guide

Get up and running with Apathetic Python Testing in minutes.

## Basic Usage

The simplest way to use Apathetic Python Testing is to import the functions you need:

```python
from apathetic_testing import load_jsonc, load_toml, is_ci, detect_runtime_mode
from pathlib import Path

# Load configuration files
config = load_jsonc(Path("config.jsonc"))
pyproject = load_toml(Path("pyproject.toml"))

# Detect environment
if is_ci():
    print("Running in CI environment")

# Detect runtime mode
mode = detect_runtime_mode("my_package")
print(f"Running in {mode} mode")
```

## File Loading

### Loading JSONC Files

JSONC (JSON with Comments) files are commonly used for configuration:

```python
from apathetic_testing import load_jsonc
from pathlib import Path

# Load a JSONC file
config = load_jsonc(Path("config.jsonc"))
# Returns dict or list, or None if file is empty/only comments
```

### Loading TOML Files

TOML files are supported with automatic fallback to `tomli` on Python 3.10:

```python
from apathetic_testing import load_toml
from pathlib import Path

# Load a TOML file
pyproject = load_toml(Path("pyproject.toml"), required=True)
# Returns dict or None if unavailable (unless required=True)
```

## System Detection

### CI Environment Detection

Check if your code is running in a CI environment:

```python
from apathetic_testing import is_ci

if is_ci():
    print("Running in CI")
    # Adjust behavior for CI environment
else:
    print("Running locally")
```

### Pytest Detection

Detect if code is running under pytest:

```python
from apathetic_testing import is_running_under_pytest

if is_running_under_pytest():
    # Use test-specific configuration
    pass
```

### Runtime Mode Detection

Detect how your package is being executed:

```python
from apathetic_testing import detect_runtime_mode

mode = detect_runtime_mode("my_package")
# Returns: "package", "stitched", "zipapp", or "frozen"
```

## Path Utilities

### Path Normalization

Normalize paths for cross-platform use:

```python
from apathetic_testing import normalize_path_string

# Normalize Windows paths to forward slashes
path = normalize_path_string("src\\utils\\file.py")
# Returns: "src/utils/file.py"
```

### Glob Pattern Handling

Work with glob patterns:

```python
from apathetic_testing import has_glob_chars, get_glob_root

# Check if a string contains glob characters
if has_glob_chars("src/**/*.py"):
    print("Contains glob pattern")

# Get the non-glob portion of a path
root = get_glob_root("src/**/*.txt")
# Returns: Path("src")
```

## Pattern Matching

### Portable Glob Matching

Match paths against glob patterns with recursive `**` support:

```python
from apathetic_testing import fnmatchcase_portable

# Match paths against patterns
if fnmatchcase_portable("src/utils/file.py", "src/**/*.py"):
    print("Match!")

# Works with recursive patterns on Python 3.10+
if fnmatchcase_portable("deep/nested/file.py", "**/*.py"):
    print("Recursive match!")
```

### Exclusion Checking

Check if a path matches exclusion patterns:

```python
from apathetic_testing import is_excluded_raw
from pathlib import Path

patterns = ["**/__pycache__/**", "*.pyc", "tests/**"]
root = Path(".")

if is_excluded_raw("src/__pycache__/file.pyc", patterns, root):
    print("File is excluded")
```

## Text Processing

### Pluralization

Get the correct plural suffix:

```python
from apathetic_testing import plural

count = 5
print(f"{count} file{plural(count)}")  # "5 files"

count = 1
print(f"{count} file{plural(count)}")  # "1 file"
```

### Error Message Cleanup

Remove redundant path mentions from error messages:

```python
from apathetic_testing import remove_path_in_error_message
from pathlib import Path

error_msg = "Invalid JSONC syntax in /path/to/config.jsonc: Expecting value"
path = Path("/path/to/config.jsonc")

clean_msg = remove_path_in_error_message(error_msg, path)
# Returns: "Invalid JSONC syntax: Expecting value"
```

## Type Utilities

### Safe isinstance Checks

Check types safely for TypedDicts and generics:

```python
from apathetic_testing import safe_isinstance
from typing import TypedDict

class Config(TypedDict):
    name: str
    value: int

data = {"name": "test", "value": 42}

# Works with TypedDict
if safe_isinstance(data, Config):
    print("Valid config")

# Works with generics
if safe_isinstance([1, 2, 3], list[int]):
    print("List of integers")
```

### Literal Type Extraction

Extract values from Literal types:

```python
from apathetic_testing import literal_to_set
from typing import Literal

Mode = Literal["dev", "prod", "test"]
valid_modes = literal_to_set(Mode)
# Returns: {"dev", "prod", "test"}
```

## Output Capture

Capture stdout and stderr from CLI commands:

```python
from apathetic_testing import capture_output
import sys

with capture_output() as cap:
    print("Hello, world!")
    print("Error message", file=sys.stderr)

# Access captured output
print(f"stdout: {cap.stdout.getvalue()}")
print(f"stderr: {cap.stderr.getvalue()}")
print(f"merged: {cap.merged.getvalue()}")

# Or convert to dict
output = cap.as_dict()
```

## Using the Namespace Class

All utilities are also available through the namespace class:

```python
from apathetic_testing import apathetic_testing

# Use via namespace
config = apathetic_testing.load_jsonc(Path("config.jsonc"))
is_ci = apathetic_testing.is_ci()
```

## Next Steps

- Read the [API Reference]({{ '/api' | relative_url }}) for complete documentation
- Check out [Examples]({{ '/examples' | relative_url }}) for more advanced patterns
- See [Contributing]({{ '/contributing' | relative_url }}) if you want to help improve the project
