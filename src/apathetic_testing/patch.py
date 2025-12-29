# src/apathetic_testing/patch.py
"""Patching utilities mixin for monkeypatching functions."""

from __future__ import annotations

import sys
from collections.abc import Callable, Sequence
from types import ModuleType
from typing import TYPE_CHECKING, Any

from apathetic_logging import safeTrace


if TYPE_CHECKING:
    import pytest

from .runtime import ApatheticTest_Internal_Runtime


class ApatheticTest_Internal_Patch:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Mixin class providing patching utilities."""

    @staticmethod
    def patch_everywhere(  # noqa: C901, PLR0912, PLR0915
        mp: pytest.MonkeyPatch,
        mod_env: ModuleType | Any,
        func_name: str,
        replacement_func: Callable[..., object],
        *,
        package_prefix: str | Sequence[str],
        stitch_hints: set[str] | None = None,
        create_if_missing: bool = False,
        caller_func_name: str | None = None,
    ) -> None:
        """Replace a function everywhere it was imported.

        Works in both package and stitched single-file runtimes.
        Walks sys.modules once and handles:
          • the defining module
          • any other module that imported the same function object
          • any freshly reloaded stitched modules (heuristic: path matches hints)

        Args:
            mp: pytest.MonkeyPatch instance to use for patching
            mod_env: Module or object containing the function to patch
            func_name: Name of the function to patch
            replacement_func: Function to replace the original with
            package_prefix: Package name prefix(es) to filter modules.
                Can be a single string (e.g., "apathetic_testing") or a sequence
                of strings (e.g., ["apathetic_testing", "my_package"]) to patch
                across multiple packages.
            stitch_hints: Set of path hints to identify stitched modules.
                Defaults to {"/dist/", "stitched"}. When providing custom
                hints, you must be certain of the path attributes of your
                stitched file, as this uses substring matching on the module's
                __file__ path. This is a heuristic fallback when identity
                checks fail (e.g., when modules are reloaded).
            create_if_missing: If True, create the attribute if it doesn't exist.
                If False (default), raise TypeError if the function doesn't exist.
            caller_func_name: If provided, only patch __globals__ for this specific
                function. If None (default), patch __globals__ for all functions in
                the module that reference the original function.
        """
        if stitch_hints is None:
            stitch_hints = {"/dist/", "stitched"}

        # --- Sanity checks ---
        func = getattr(mod_env, func_name, None)
        func_existed = func is not None

        if func is None:
            if create_if_missing:
                # Will create the function below, but don't set func to replacement_func
                # since we need to track that it didn't exist for search logic
                pass
            else:
                xmsg = f"Could not find {func_name!r} on {mod_env!r}"
                raise TypeError(xmsg)

        mod_name = getattr(mod_env, "__name__", type(mod_env).__name__)

        # Patch in the defining module
        # For modules, if the attribute doesn't exist and create_if_missing=True,
        # we need to create it manually first, then use monkeypatch to track it
        if not func_existed and isinstance(mod_env, ModuleType):
            # Manually create the attribute on the module's __dict__
            # This is necessary because monkeypatch.setattr may fail if the attribute
            # doesn't exist on a module
            mod_env.__dict__[func_name] = replacement_func
            # Now register with monkeypatch for cleanup on undo
            # Since the attribute now exists, setattr should work
            mp.setattr(mod_env, func_name, replacement_func)
            safeTrace(f"Patched {mod_name}.{func_name}")
        else:
            try:
                mp.setattr(mod_env, func_name, replacement_func)
            except AttributeError:
                # If setattr fails because attribute doesn't exist on a module,
                # create it manually and try again
                if isinstance(mod_env, ModuleType) and create_if_missing:
                    mod_env.__dict__[func_name] = replacement_func
                    mp.setattr(mod_env, func_name, replacement_func)
                    safeTrace(f"Created and patched {mod_name}.{func_name}")
                else:
                    raise
            if func_existed:
                safeTrace(f"Patched {mod_name}.{func_name}")
            else:
                safeTrace(f"Created and patched {mod_name}.{func_name}")

        # Patch direct function calls via __globals__
        # In package mode, module-level functions reference their module's __dict__
        # as __globals__. We patch __globals__ to intercept direct calls (e.g.,
        # func()) which resolve through __globals__, not module attributes.
        #
        # In stitched mode (e.g., serger's stub architecture), the situation is more
        # complex: stub modules have a separate __dict__ from the stitched file's
        # __globals__. When serger creates stub modules via types.ModuleType, it
        # copies values from stitched __globals__ to the stub's __dict__. Functions
        # defined in the stitched file use the stitched file's __globals__ for
        # direct calls, NOT the stub's __dict__. Therefore, patching BOTH the stub
        # module (via setattr) AND __globals__ is necessary to intercept all call
        # patterns. MonkeyPatch's undo stack properly restores patched values,
        # ensuring test isolation is preserved even with shared __globals__.
        is_stitched_or_zipapp = False
        if isinstance(mod_env, ModuleType):
            # Check if module is stitched or zipapp
            mode = ApatheticTest_Internal_Runtime.detect_module_runtime_mode(
                mod_env,
                stitch_hints=stitch_hints,
            )
            is_stitched_or_zipapp = mode in ("stitched", "zipapp")

        if func_existed and isinstance(mod_env, ModuleType) and func is not None:
            _apathetic_testing_priv_patch_globals_for_direct_calls(
                mp=mp,
                mod=mod_env,
                func_name=func_name,
                original_func=func,
                replacement_func=replacement_func,
                safeTrace=safeTrace,
                caller_func_name=caller_func_name,
            )

        patched_ids: set[int] = set()

        for m in list(sys.modules.values()):
            if (
                m is mod_env
                or not isinstance(m, ModuleType)  # pyright: ignore[reportUnnecessaryIsInstance]
                or not hasattr(m, "__dict__")
            ):
                continue

            # skip irrelevant stdlib or third-party modules for performance
            name = getattr(m, "__name__", "")
            if isinstance(package_prefix, str):
                prefixes: Sequence[str] = (package_prefix,)
            else:
                prefixes = package_prefix
            if not any(name.startswith(prefix) for prefix in prefixes):
                continue

            did_patch = False

            # 1) Normal case: module imported the same object
            # Only search if the function actually existed (not created)
            if func_existed:
                for k, v in list(m.__dict__.items()):
                    if v is func:
                        mp.setattr(m, k, replacement_func)
                        did_patch = True

            # 2) Single-file/zipapp case: reloaded stitched modules or zipapp modules
            #    Check for __STITCHED__ marker first (most reliable), then fallback
            #    to path heuristics
            mode = ApatheticTest_Internal_Runtime.detect_module_runtime_mode(
                m,
                stitch_hints=stitch_hints,
            )
            is_stitched_or_zipapp = mode in ("stitched", "zipapp")
            if is_stitched_or_zipapp and hasattr(m, func_name):
                mp.setattr(m, func_name, replacement_func)

                # CRITICAL: Also patch __globals__ for stitched modules.
                # This handles the case where a stitched file (e.g., serger) creates
                # stub modules and calls functions with direct calls (e.g., func()).
                # The stub module's __dict__ is a separate dictionary from the
                # stitched file's __globals__. Direct calls resolve through __globals__,
                # not the stub's __dict__. Therefore, patching only via setattr is
                # insufficient - we must also patch __globals__ to intercept direct
                # calls within the stitched functions. MonkeyPatch's undo stack ensures
                # proper restoration and test isolation even for shared __globals__.
                if func_existed and func is not None:
                    _apathetic_testing_priv_patch_globals_for_direct_calls(
                        mp=mp,
                        mod=m,
                        func_name=func_name,
                        original_func=func,
                        replacement_func=replacement_func,
                        safeTrace=safeTrace,
                        caller_func_name=caller_func_name,
                    )
                did_patch = True

            if did_patch and id(m) not in patched_ids:
                patched_ids.add(id(m))
                safeTrace(f"  also patched {name}")


def _apathetic_testing_priv_patch_globals_for_direct_calls(
    *,
    mp: pytest.MonkeyPatch,
    mod: ModuleType,
    func_name: str,
    original_func: Callable[..., object],
    replacement_func: Callable[..., object],
    safeTrace: Callable[..., None],  # noqa: N803
    caller_func_name: str | None = None,
) -> None:
    """Replace a function everywhere it was imported.

    Works in both package and stitched single-file runtimes.
    Walks sys.modules once and handles:
      • the defining module
      • any other module that imported the same function object
      • any freshly reloaded stitched modules (heuristic: path matches hints)

    Args:
        mp: pytest.MonkeyPatch instance to use for patching
        mod: Module containing the function to patch
        func_name: Name of the function to patch
        original_func: The original function object to replace
        replacement_func: Function to replace the original with
        safeTrace: Callable for safe tracing/logging operations
        caller_func_name: If provided, only patch __globals__ for this specific
            function. If None (default), patch __globals__ for all functions in
            the module that reference the original function.
    """
    patched_count = 0
    for name, obj in mod.__dict__.items():
        if not callable(obj):
            continue
        if caller_func_name and name != caller_func_name:
            continue
        if not hasattr(obj, "__globals__"):
            continue
        # Get __globals__ and check if it's actually a dict
        try:
            globals_dict = obj.__globals__
        except (TypeError, AttributeError):
            # __globals__ might be a descriptor or not accessible
            continue
        if not isinstance(globals_dict, dict):  # pyright: ignore[reportUnnecessaryIsInstance]
            # __globals__ is not a dict (could be a descriptor)
            continue
        # Check if this function's __globals__ references the original function
        if func_name in globals_dict:
            current_ref = globals_dict[func_name]
            if current_ref is original_func:
                # Use mp.setitem() to ensure proper restoration when test completes
                # This is critical for test isolation - without it, __globals__
                # modifications persist and affect subsequent tests
                mp.setitem(globals_dict, func_name, replacement_func)
                patched_count += 1
                safeTrace(
                    f"  patched __globals__ for {name}()",
                    f"original_id={id(original_func)}",
                    f"replacement_id={id(replacement_func)}",
                )
            else:
                safeTrace(
                    f"  ⏭️  skipped __globals__ for {name}()",
                    "reference mismatch",
                )
    if patched_count > 0:
        safeTrace(
            f"  patched __globals__ for {patched_count} function(s) in {mod.__name__}"
        )
