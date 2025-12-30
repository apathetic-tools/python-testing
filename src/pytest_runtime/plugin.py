"""Pytest plugin for runtime mode filtering and reporting."""

from __future__ import annotations

import os

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add custom CLI options for runtime mode selection."""
    parser.addoption(
        "--runtime",
        action="store",
        default=None,
        help=(
            "Specify runtime mode (package, stitched, zipapp). "
            "Can also be set via RUNTIME_MODE environment variable. "
            "CLI flag takes precedence if both are set."
        ),
    )


def _mode() -> str:
    return os.getenv("RUNTIME_MODE", "package")


def _filter_runtime_mode_tests(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    mode = _mode()
    # Check if verbose mode is enabled (verbose > 0 means user wants verbose output)
    verbose = getattr(config.option, "verbose", 0)
    is_quiet = verbose <= 0

    # Only track included tests if not in quiet mode (for later reporting)
    included_map: dict[str, int] | None = {} if not is_quiet else None
    root = str(config.rootpath)
    testpaths: list[str] = config.getini("testpaths") or []

    # Identify mode-specific files by a custom variable defined at module scope
    for item in list(items):
        mod = item.getparent(pytest.Module)
        if mod is None or not hasattr(mod, "obj"):
            continue

        runtime_marker = getattr(mod.obj, "__runtime_mode__", None)

        if runtime_marker and runtime_marker != mode:
            items.remove(item)
            continue

        # Only track if not in quiet mode
        if runtime_marker and runtime_marker == mode and included_map is not None:
            file_path = str(item.fspath)
            # Make path relative to project root dir
            if file_path.startswith(root):
                file_path = os.path.relpath(file_path, root)
                for tp in testpaths:
                    if file_path.startswith(tp.rstrip("/") + os.sep):
                        file_path = file_path[len(tp.rstrip("/") + os.sep) :]
                        break

            included_map[file_path] = included_map.get(file_path, 0) + 1

    # Store results for later reporting (only if not in quiet mode)
    if included_map is not None:
        config._included_map = included_map  # type: ignore[attr-defined]  # noqa: SLF001
        config._runtime_mode = mode  # type: ignore[attr-defined]  # noqa: SLF001


def pytest_report_header(config: pytest.Config) -> str:  # noqa: ARG001 # pyright: ignore[reportUnknownParameterType]
    mode = _mode()
    return f"Runtime mode: {mode}"


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """Filter and record runtime-specific tests for later reporting.

    Debug test filtering is handled by the pytest_debug plugin.
    """
    _filter_runtime_mode_tests(config, items)


def pytest_unconfigure(config: pytest.Config) -> None:
    """Print summary of included runtime-specific tests at the end."""
    included_map: dict[str, int] = getattr(config, "_included_map", {})
    mode = getattr(config, "_runtime_mode", "package")

    if not included_map:
        return

    # Only print if pytest is not in quiet mode (verbose > 0 means verbose mode)
    verbose = getattr(config.option, "verbose", 0)
    if verbose <= 0:
        return

    total_tests = sum(included_map.values())
    print(  # noqa: T201
        f"🧪 Included {total_tests} {mode}-specific tests"
        f" across {len(included_map)} files:",
    )
    for path, count in sorted(included_map.items()):
        print(f"   • ({count}) {path}")  # noqa: T201


__all__ = [
    "pytest_addoption",
    "pytest_collection_modifyitems",
    "pytest_report_header",
    "pytest_unconfigure",
]
