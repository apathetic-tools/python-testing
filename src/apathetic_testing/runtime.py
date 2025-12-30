# src/apathetic_testing/runtime.py
"""Build and runtime utilities for testing.

This module provides test infrastructure for multi-runtime testing (package,
stitched, zipapp). Note the distinction between functions in this module and
those in apathetic-utils:

**apathetic-testing** (this module):
- `detect_module_runtime_mode()` — Detects which runtime a specific MODULE was
  loaded from. Used in test infrastructure to verify correct module loading
  across different build modes. Needed only in dev environments.

**apathetic-utils** (runtime dependency):
- `detect_runtime_mode()` — Detects which runtime the current PROCESS is
  executing under. Used by CLI tools for features like --version, CI detection,
  etc. Needed at runtime by end-user applications.

The separation reflects their different purposes and dependency contexts:
apathetic-testing is a devDependency (testing only), while apathetic-utils
is a runtime dependency (used by CLI tools that depend on it).
"""

from __future__ import annotations

import importlib
import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
from apathetic_logging import makeSafeTrace
from apathetic_utils import find_all_packages_under_path, find_python_command, load_toml


class ApatheticTest_Internal_Runtime:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class providing build and runtime utilities for testing."""

    @staticmethod
    def detect_module_runtime_mode(
        mod: ModuleType,
        *,
        stitch_hints: set[str] | None = None,
    ) -> str:
        """Detect the runtime mode of a specific module.

        Determines whether a module was built as part of a stitched single-file
        script, zipapp archive, or standard package by checking for markers and
        file path attributes.

        This check prioritizes marker-based detection (most reliable) but falls
        back to path heuristics for edge cases. It works correctly in:
        - Stitched mode: Modules loaded from a .py stitched script
        - Zipapp mode: Modules loaded from a .pyz zipapp archive
        - Package mode: Regular package modules
        - Mixed scenarios: When testing a stitched module while running in package mode

        Args:
            mod: Module to check
            stitch_hints: Optional set of path hints to identify stitched modules.
                Defaults to {"/dist/", "stitched"}. Used as fallback when markers
                are not present.

        Returns:
            - "stitched" if module has __STITCHED__ or __STANDALONE__ marker,
              or __file__ path matches stitch_hints
            - "zipapp" if module __file__ indicates zipapp (contains .pyz)
            - "package" for regular package modules

        Raises:
            TypeError: If mod is not a ModuleType
        """
        if stitch_hints is None:
            stitch_hints = {"/dist/", "stitched"}

        if not isinstance(mod, ModuleType):  # pyright: ignore[reportUnnecessaryIsInstance]
            msg = f"Expected ModuleType, got {type(mod).__name__}"
            raise TypeError(msg)

        # Check for stitched markers first (most reliable)
        if hasattr(mod, "__STITCHED__"):
            return "stitched"

        # Check for zipapp and stitched by looking at __file__ path
        file_path = getattr(mod, "__file__", "") or ""
        if ".pyz/" in file_path or file_path.endswith(".pyz"):
            return "zipapp"
        if any(h in file_path for h in stitch_hints):
            return "stitched"

        # Default to package mode
        return "package"

    @staticmethod
    def _parse_cli_flag(flag_name: str) -> str | None:
        """Parse CLI flag from sys.argv.

        Supports both --flag=value and --flag value formats.

        Args:
            flag_name: Name of the flag (without -- prefix)

        Returns:
            Flag value if found, None otherwise
        """
        flag_with_dashes = f"--{flag_name}"
        flag_with_equals = f"--{flag_name}="

        for i, arg in enumerate(sys.argv):
            # Check for --flag=value format
            if arg.startswith(flag_with_equals):
                return arg[len(flag_with_equals) :]
            # Check for --flag value format
            if arg == flag_with_dashes and i + 1 < len(sys.argv):
                return sys.argv[i + 1]

        return None

    @staticmethod
    def _check_needs_rebuild(output_path: Path, src_dir: Path) -> bool:
        """Check if output file needs to be rebuilt.

        Args:
            output_path: Path to the output file
            src_dir: Directory containing source files to check

        Returns:
            True if rebuild is needed, False otherwise
        """
        if not output_path.exists():
            return True
        output_mtime_ns = output_path.stat().st_mtime_ns
        for src_file in src_dir.rglob("*.py"):
            if src_file.stat().st_mtime_ns > output_mtime_ns:
                return True
        return False

    @staticmethod
    def _validate_build_output(output_path: Path, build_type: str) -> None:
        """Validate that build output was created successfully.

        Args:
            output_path: Path to the output file
            build_type: Type of build (e.g., "stitched script", "zipapp")

        Raises:
            RuntimeError: If output file doesn't exist after build
        """
        # Force mtime update in case contents identical
        output_path.touch()
        if not output_path.exists():
            msg = f"❌ Failed to generate {build_type}."
            raise RuntimeError(msg)

    @staticmethod
    def _run_bundler_script(
        root: Path,
        command_path: str | None,
        output_path: Path,
        build_type: str,
    ) -> bool:
        """Run a custom bundler script if provided and exists.

        Args:
            root: Project root directory
            command_path: Optional path to bundler script (relative to root)
            output_path: Path to the expected output file
            build_type: Type of build (e.g., "stitched script", "zipapp")

        Returns:
            True if bundler script was run successfully,
            False if not provided or doesn't exist
        """
        if command_path is None:
            return False

        bundler_path = root / command_path
        if not bundler_path.exists():
            return False

        print(  # noqa: T201
            f"⚙️  Rebuilding {build_type} (python {command_path})..."
        )
        subprocess.run(  # noqa: S603
            [sys.executable, str(bundler_path)],
            check=True,
            cwd=root,
        )
        ApatheticTest_Internal_Runtime._validate_build_output(output_path, build_type)
        return True

    @staticmethod
    def ensure_stitched_script_up_to_date(
        *,
        root: Path,
        script_name: str | None = None,
        package_name: str,
        command_path: str | None = None,
        log_level: str | None = None,
    ) -> Path:
        """Rebuild stitched script if missing or outdated.

        Args:
            root: Project root directory
            script_name: Optional name of the stitched script (without .py extension).
                If None, defaults to package_name.
            package_name: Name of the package (e.g., "apathetic_testing")
            command_path: Optional path to bundler script (relative to root).
                If provided and exists, uses `python {command_path}`.
                Otherwise, uses `python -m serger --config .serger.jsonc`.
            log_level: Optional log level to pass to serger.
                If provided, adds `--log-level=<log_level>` to the serger command.

        Returns:
            Path to the stitched script
        """
        # Use package_name as default if script_name not provided
        actual_script_name = package_name if script_name is None else script_name
        bin_path = root / "dist" / f"{actual_script_name}.py"
        src_dir = root / "src" / package_name

        # Check if rebuild is needed
        needs_rebuild = ApatheticTest_Internal_Runtime._check_needs_rebuild(
            bin_path, src_dir
        )

        if needs_rebuild:
            # Check if command_path is provided and exists
            if ApatheticTest_Internal_Runtime._run_bundler_script(
                root, command_path, bin_path, "stitched script"
            ):
                return bin_path

            # Fall back to using serger (found via find_python_command)
            config_path = root / ".serger.jsonc"
            if not config_path.exists():
                msg = (
                    "❌ Failed to generate stitched script: "
                    f"serger config not found at {config_path}."
                )
                raise RuntimeError(msg)

            print("⚙️  Rebuilding stitched bundle (serger)...")  # noqa: T201
            serger_cmd = find_python_command(
                "serger",
                error_hint=(
                    "serger not found. "
                    "Ensure serger is installed in your virtual environment."
                ),
            )
            serger_cmd.extend(["--config", str(config_path)])
            if log_level is not None:
                serger_cmd.extend(["--log-level", log_level])
            subprocess.run(  # noqa: S603
                serger_cmd,
                check=True,
                cwd=root,
            )
            ApatheticTest_Internal_Runtime._validate_build_output(
                bin_path, "stitched script"
            )

        return bin_path

    @staticmethod
    def ensure_zipapp_up_to_date(
        *,
        root: Path,
        script_name: str | None = None,
        package_name: str,
        command_path: str | None = None,
        log_level: str | None = None,
    ) -> Path:
        """Rebuild zipapp if missing or outdated.

        Args:
            root: Project root directory
            script_name: Optional name of the zipapp (without .pyz extension).
                If None, defaults to package_name.
            package_name: Name of the package (e.g., "apathetic_testing")
            command_path: Optional path to bundler script (relative to root).
                If provided and exists, uses `python {command_path}`.
                Otherwise, uses zipbundler.
            log_level: Optional log level to pass to zipbundler.
                If provided, adds `--log-level=<log_level>` to the zipbundler command.

        Returns:
            Path to the zipapp
        """
        # Use package_name as default if script_name not provided
        actual_script_name = package_name if script_name is None else script_name
        zipapp_path = root / "dist" / f"{actual_script_name}.pyz"
        src_dir = root / "src" / package_name

        # Check if rebuild is needed
        needs_rebuild = ApatheticTest_Internal_Runtime._check_needs_rebuild(
            zipapp_path, src_dir
        )

        if needs_rebuild:
            # Check if command_path is provided and exists
            if ApatheticTest_Internal_Runtime._run_bundler_script(
                root, command_path, zipapp_path, "zipapp"
            ):
                return zipapp_path

            # Fall back to using zipbundler
            zipbundler_cmd = find_python_command(
                "zipbundler",
                error_hint=(
                    "zipbundler not found. "
                    "Ensure zipbundler is installed: poetry install --with dev"
                ),
            )
            print("⚙️  Rebuilding zipapp (zipbundler)...")  # noqa: T201
            cmd = [
                *zipbundler_cmd,
                "-m",
                package_name,
                "-o",
                str(zipapp_path),
                "-q",
                ".",
            ]
            if log_level is not None:
                cmd.extend(["--log-level", log_level])
            subprocess.run(  # noqa: S603
                cmd,
                cwd=root,
                check=True,
            )
            ApatheticTest_Internal_Runtime._validate_build_output(zipapp_path, "zipapp")

        return zipapp_path

    @staticmethod
    def _find_project_root() -> Path:
        """Find project root with priority: env var > git root > CWD.

        Priority order:
        1. PROJ_ROOT environment variable (explicit override)
        2. Walk up directories looking for .git (file or dir, handles submodules)
        3. Current working directory (fallback)

        Returns:
            Path to project root directory
        """
        # Priority 1: Explicit env var override
        env_root = os.getenv("PROJ_ROOT")
        if env_root:
            return Path(env_root).resolve()

        # Priority 2: Look for .git by walking up from CWD
        # (handles both regular repos and submodules)
        current = Path.cwd().resolve()
        for parent in [current, *current.parents]:
            git_path = parent / ".git"
            if git_path.exists():
                # .git can be a directory (regular repo) or file (submodule)
                return parent

        # Priority 3: Current working directory (fallback)
        return Path.cwd().resolve()

    @staticmethod
    def _get_package_name_from_pyproject(root: Path) -> str | None:
        """Extract package name from pyproject.toml.

        Reads project.name from pyproject.toml and normalizes hyphens to
        underscores for Python import compatibility.

        Args:
            root: Project root directory containing pyproject.toml

        Returns:
            Normalized package name (hyphens → underscores), or None if not found
        """
        pyproject_path = root / "pyproject.toml"
        if not pyproject_path.exists():
            return None

        try:
            data = load_toml(pyproject_path)
            if data is None:
                return None
            project_name = data.get("project", {}).get("name")
            if isinstance(project_name, str):
                # Normalize hyphens to underscores for Python imports
                return project_name.replace("-", "_")
        except (ValueError, RuntimeError):
            # Errors parsing TOML
            return None

        return None

    @staticmethod
    def runtime_swap(
        *,
        root: Path | None = None,
        package_name: str | None = None,
        script_name: str | None = None,
        stitch_command: str | None = None,
        zipapp_command: str | None = None,
        mode: str | None = None,
        cli_flag: bool = True,
        cli_flag_name: str = "runtime",
        log_level: str | None = None,
    ) -> bool:
        """Pre-import hook — runs before any tests or plugins are imported.

        Swaps in the appropriate runtime module based on mode:
        - package (default): uses src/{package_name} (no swap needed)
        - stitched: uses dist/{script_name}.py (serger-built single file)
        - zipapp: uses dist/{script_name}.pyz (zipbundler-built zipapp)

        This ensures all test imports work transparently regardless of runtime mode.

        Args:
            root: Project root directory. If None, auto-detects by looking for git
                repository root, then falls back to current working directory.
            package_name: Name of the package (e.g., "apathetic_testing"). If None,
                attempts to read from pyproject.toml [project] name field.
            script_name: Optional name of the distributed script (without extension).
                If None, defaults to package_name.
            stitch_command: Optional path to bundler script for stitched mode
                (relative to root). If provided and exists, uses
                `python {stitch_command}`. Otherwise, uses
                `python -m serger --config .serger.jsonc`.
            zipapp_command: Optional path to bundler script for zipapp mode
                (relative to root). If provided and exists, uses
                `python {zipapp_command}`. Otherwise, uses zipbundler.
            mode: Explicit runtime mode override. Takes highest priority.
                If provided, uses this value regardless of CLI or env var.
            cli_flag: If True, check sys.argv for the CLI flag (default True).
                Used if mode is None.
            cli_flag_name: Name of the CLI flag to check (default "runtime-mode").
                Supports both --flag=value and --flag value formats.
            log_level: Optional log level to pass to serger and zipbundler.
                If provided, adds `--log-level=<log_level>` to their commands.

        Returns:
            True if swap was performed, False if in package mode

        Raises:
            pytest.UsageError: If mode is invalid, package_name cannot be determined,
                or build fails
        """
        if root is None:
            root = ApatheticTest_Internal_Runtime._find_project_root()

        if package_name is None:
            package_name = (
                ApatheticTest_Internal_Runtime._get_package_name_from_pyproject(root)
            )
            if package_name is None:
                msg = (
                    "package_name not provided and could not be read from "
                    f"pyproject.toml at {root / 'pyproject.toml'}"
                )
                raise pytest.UsageError(msg)

        safe_trace = makeSafeTrace("🧬")

        # Priority: mode > CLI flag > env var
        runtime_mode = mode
        if runtime_mode is None and cli_flag:
            runtime_mode = ApatheticTest_Internal_Runtime._parse_cli_flag(cli_flag_name)
        if runtime_mode is None:
            runtime_mode = os.getenv("RUNTIME_MODE", "package")

        if runtime_mode == "package":
            return False  # Normal package mode; nothing to do.

        # Nuke any already-imported modules from src/ to avoid stale refs.
        # Dynamically detect all modules under src/ instead of hardcoding names.
        src_dir = root / "src"
        modules_to_nuke = find_all_packages_under_path(src_dir)

        for name in list(sys.modules):
            # Check if module name matches any detected module or is a submodule
            for mod_name in modules_to_nuke:
                if name == mod_name or name.startswith(f"{mod_name}."):
                    del sys.modules[name]
                    break

        if runtime_mode == "stitched":
            return ApatheticTest_Internal_Runtime._load_stitched_mode(
                root, package_name, script_name, stitch_command, safe_trace, log_level
            )
        if runtime_mode == "zipapp":
            return ApatheticTest_Internal_Runtime._load_zipapp_mode(
                root, package_name, script_name, zipapp_command, safe_trace, log_level
            )

        # Unknown mode
        xmsg = (
            f"Unknown runtime mode={runtime_mode!r}. "
            "Valid modes: package, stitched, zipapp"
        )
        raise pytest.UsageError(xmsg)

    @staticmethod
    def _load_stitched_mode(
        root: Path,
        package_name: str,
        script_name: str | None,
        command_path: str | None,
        safe_trace: Any,
        log_level: str | None = None,
    ) -> bool:
        """Load stitched single-file script mode."""
        bin_path = ApatheticTest_Internal_Runtime.ensure_stitched_script_up_to_date(
            root=root,
            script_name=script_name,
            package_name=package_name,
            command_path=command_path,
            log_level=log_level,
        )

        if not bin_path.exists():
            if command_path is None:
                hint_msg = (
                    "Hint: run the bundler (e.g. `poetry run poe build:stitched`)."
                )
            else:
                hint_msg = (
                    f"Hint: run the bundler (e.g. `python {command_path}` "
                    f"or `poetry run poe build:stitched`)."
                )
            xmsg = (
                f"RUNTIME_MODE=stitched but stitched script not found "
                f"at {bin_path}.\n{hint_msg}"
            )
            raise pytest.UsageError(xmsg)

        # Load stitched script as the package.
        spec = importlib.util.spec_from_file_location(package_name, bin_path)
        if not spec or not spec.loader:
            xmsg = f"Could not create import spec for {bin_path}"
            raise pytest.UsageError(xmsg)

        try:
            mod: ModuleType = importlib.util.module_from_spec(spec)
            sys.modules[package_name] = mod
            spec.loader.exec_module(mod)
            safe_trace(f"Loaded stitched module from {bin_path}")
        except Exception as e:
            # Fail fast with context; this is a config/runtime problem.
            error_name = type(e).__name__
            xmsg = (
                f"Failed to import stitched module from {bin_path}.\n"
                f"Original error: {error_name}: {e}\n"
                f"Tip: rebuild the bundle and re-run."
            )
            raise pytest.UsageError(xmsg) from e

        safe_trace(f"✅ Loaded stitched runtime early from {bin_path}")
        return True

    @staticmethod
    def _load_zipapp_mode(
        root: Path,
        package_name: str,
        script_name: str | None,
        command_path: str | None,
        safe_trace: Any,
        log_level: str | None = None,
    ) -> bool:
        """Load zipapp mode.

        Handles zipbundler zipapps which store packages directly in the zip root.
        Python's standard zipimporter can handle this structure directly.
        """
        zipapp_path = ApatheticTest_Internal_Runtime.ensure_zipapp_up_to_date(
            root=root,
            script_name=script_name,
            package_name=package_name,
            command_path=command_path,
            log_level=log_level,
        )

        if not zipapp_path.exists():
            xmsg = (
                f"RUNTIME_MODE=zipapp but zipapp not found at {zipapp_path}.\n"
                f"Hint: run `poetry run poe build:zipapp`."
            )
            raise pytest.UsageError(xmsg)

        # For zipbundler zipapps, use normal import
        zipapp_str = str(zipapp_path)
        if zipapp_str not in sys.path:
            sys.path.insert(0, zipapp_str)

        try:
            importlib.import_module(package_name)
            safe_trace(f"Loaded zipapp module from {zipapp_path}")
        except Exception as e:
            error_name = type(e).__name__
            xmsg = (
                f"Failed to import zipapp module from {zipapp_path}.\n"
                f"Original error: {error_name}: {e}\n"
                f"Tip: rebuild the zipapp and re-run."
            )
            raise pytest.UsageError(xmsg) from e

        safe_trace(f"✅ Loaded zipapp runtime early from {zipapp_path}")
        return True
