# tests/30_independant/test_fnmatchcase_portable.py
"""Tests for fnmatchcase_portable utility function.

fnmatchcase_portable() is a drop-in replacement for fnmatch.fnmatch that:
- Always uses case-sensitive matching (via fnmatchcase from stdlib)
- Backports Python 3.11's recursive '**' support to Python 3.10
- Uses the Python stdlib's fnmatchcase for non-** patterns
- Handles *, **, ?, and [] glob patterns

IMPORTANT: fnmatchcase (unlike shell globbing) does allow * to cross directory
separators. This function is designed for gitignore-style pattern matching,
not shell glob semantics.
"""

import sys
from fnmatch import fnmatchcase
from types import SimpleNamespace

import pytest

import apathetic_testing as mod_autils
import apathetic_testing.matching as amod_utils_matching
from tests.utils.constants import PATCH_STITCH_HINTS, PROGRAM_PACKAGE


def test_fnmatchcase_portable_literal_match() -> None:
    """Exact string matching without glob characters."""
    # --- execute + verify ---
    assert mod_autils.fnmatchcase_portable("src/main.py", "src/main.py")
    assert not mod_autils.fnmatchcase_portable("src/main.py", "src/other.py")
    assert not mod_autils.fnmatchcase_portable("src/main.py", "other/main.py")


def test_fnmatchcase_portable_single_star_matches() -> None:
    """Single * matches any characters (including directory separators).

    NOTE: fnmatchcase (unlike shell globbing) allows * to cross '/'.
    This is by design for gitignore-style matching.
    """
    # --- execute + verify ---
    assert mod_autils.fnmatchcase_portable("src/main.py", "src/*.py")
    assert mod_autils.fnmatchcase_portable("src/test.py", "src/*.py")
    # fnmatchcase allows * to cross /, unlike shell globbing
    assert mod_autils.fnmatchcase_portable("src/sub/main.py", "src/*.py")
    assert not mod_autils.fnmatchcase_portable("src/main.txt", "src/*.py")


def test_fnmatchcase_portable_single_star_matches_any() -> None:
    """* matches any characters, including slashes.

    This is gitignore semantics, not shell glob semantics.
    """
    # --- execute + verify ---
    assert mod_autils.fnmatchcase_portable("main.py", "*.py")
    assert mod_autils.fnmatchcase_portable("src/main.py", "*.py")
    assert mod_autils.fnmatchcase_portable("src/sub/deep/main.py", "*.py")
    assert not mod_autils.fnmatchcase_portable("main.txt", "*.py")


def test_fnmatchcase_portable_double_star_matches() -> None:
    """** matches paths with at least one slash-separated segment.

    On Python 3.11+, fnmatchcase handles **. On Python 3.10, we backport it.
    ** requires at least one path component between delimiters.
    """
    # --- execute + verify ---
    # ** requires at least one segment
    assert not mod_autils.fnmatchcase_portable("src/main.py", "src/**/main.py")

    # With intervening path
    assert mod_autils.fnmatchcase_portable("src/a/main.py", "src/**/main.py")
    assert mod_autils.fnmatchcase_portable("src/a/b/c/main.py", "src/**/main.py")
    assert not mod_autils.fnmatchcase_portable("other/a/b/c/main.py", "src/**/main.py")


def test_fnmatchcase_portable_double_star_multiple() -> None:
    """Multiple ** in one pattern."""
    # --- execute + verify ---
    assert mod_autils.fnmatchcase_portable(
        "src/a/b/test/c/d/main.py", "src/**/test/**/main.py"
    )
    # Each ** requires at least one segment
    pattern = "src/**/test/**/main.py"
    assert not mod_autils.fnmatchcase_portable("src/test/main.py", pattern)
    assert not mod_autils.fnmatchcase_portable(
        "src/a/other/c/d/main.py", "src/**/test/**/main.py"
    )


def test_fnmatchcase_portable_question_mark() -> None:
    """? matches exactly one character (including /)."""
    # --- execute + verify ---
    assert mod_autils.fnmatchcase_portable("file1.py", "file?.py")
    assert mod_autils.fnmatchcase_portable("fileA.py", "file?.py")
    assert not mod_autils.fnmatchcase_portable("file12.py", "file?.py")
    # ? can match / in fnmatchcase
    assert mod_autils.fnmatchcase_portable("file/.py", "file?.py")
    assert not mod_autils.fnmatchcase_portable("file.py", "file?.py")


def test_fnmatchcase_portable_character_class() -> None:
    """[] matches character classes."""
    # --- execute + verify ---
    assert mod_autils.fnmatchcase_portable("file1.py", "file[0-9].py")
    assert mod_autils.fnmatchcase_portable("file5.py", "file[0-9].py")
    assert not mod_autils.fnmatchcase_portable("fileA.py", "file[0-9].py")
    assert mod_autils.fnmatchcase_portable("fileA.py", "file[A-Z].py")
    assert mod_autils.fnmatchcase_portable("file1.py", "file[0-9a-z].py")


def test_fnmatchcase_portable_character_class_negation() -> None:
    """[!...] or [^...] negates a character class."""
    # --- execute + verify ---
    assert mod_autils.fnmatchcase_portable("fileA.py", "file[!0-9].py")
    assert not mod_autils.fnmatchcase_portable("file1.py", "file[!0-9].py")


def test_fnmatchcase_portable_case_sensitive() -> None:
    """Matching is always case-sensitive."""
    # --- execute + verify ---
    assert mod_autils.fnmatchcase_portable("main.py", "main.py")
    assert not mod_autils.fnmatchcase_portable("Main.py", "main.py")
    assert not mod_autils.fnmatchcase_portable("MAIN.py", "main.py")
    assert mod_autils.fnmatchcase_portable("Main.py", "Main.py")


def test_fnmatchcase_portable_empty_pattern() -> None:
    """Empty pattern matches only empty path."""
    # --- execute + verify ---
    assert mod_autils.fnmatchcase_portable("", "")
    assert not mod_autils.fnmatchcase_portable("file.py", "")
    assert not mod_autils.fnmatchcase_portable("x", "")


def test_fnmatchcase_portable_empty_path() -> None:
    """Empty path behavior with various patterns."""
    # --- execute + verify ---
    assert mod_autils.fnmatchcase_portable("", "")
    # In fnmatchcase, * matches empty string
    assert mod_autils.fnmatchcase_portable("", "*")
    # ** also matches empty string
    assert mod_autils.fnmatchcase_portable("", "**")
    assert not mod_autils.fnmatchcase_portable("", "*.py")


def test_fnmatchcase_portable_non_recursive_pattern() -> None:
    """fnmatchcase_portable() should use fnmatchcase for non-recursive patterns."""
    # This test ensures line 115 (early return for non-** patterns) is covered
    # --- execute and verify ---
    # Non-recursive patterns should use fnmatchcase directly
    assert mod_autils.fnmatchcase_portable("file.py", "*.py")
    assert mod_autils.fnmatchcase_portable("src/file.py", "src/*.py")
    assert not mod_autils.fnmatchcase_portable("file.txt", "*.py")
    assert mod_autils.fnmatchcase_portable("test_x.py", "test_?.py")


def test_fnmatchcase_portable_python_311_plus() -> None:
    """fnmatchcase_portable() should use backport for ** patterns."""
    # This test ensures ** patterns use the backport regex compiler
    # **/*.py should match files in subdirectories
    assert mod_autils.fnmatchcase_portable("src/utils/file.py", "src/**/*.py")
    assert mod_autils.fnmatchcase_portable("deep/nested/file.py", "**/*.py")
    # **/*.py requires at least one directory level, so src/file.py doesn't match
    assert not mod_autils.fnmatchcase_portable("src/file.py", "src/**/*.py")


def test_fnmatchcase_portable_no_glob_chars_delegates_to_fnmatchcase(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Patterns without ** delegate to fnmatchcase directly.

    This is an optimization: if there's no '**', we don't need the
    custom regex compiler, so we use the standard library.
    """
    # --- setup: track fnmatchcase calls ---
    call_count = 0
    original_fnmatchcase = fnmatchcase

    def counting_fnmatchcase(name: str, pattern: str) -> bool:
        nonlocal call_count
        call_count += 1
        return original_fnmatchcase(name, pattern)

    # --- patch  ---
    mod_autils.patch_everywhere(
        monkeypatch,
        amod_utils_matching,
        "fnmatchcase",
        counting_fnmatchcase,
        package_prefix=PROGRAM_PACKAGE,
        stitch_hints=PATCH_STITCH_HINTS,
    )

    # --- execute ---
    # Pattern without '**' should use fnmatchcase
    # First verify behavior works correctly
    result1 = mod_autils.fnmatchcase_portable("src/main.py", "src/*.py")
    assert result1 is True, "Function should work correctly for patterns without **"
    fnmatchcase_calls_without_double_star = call_count

    # Pattern with '**' on Python 3.10 - verify it works
    # (implementation details may vary in external package)
    fake_sys = SimpleNamespace(version_info=(3, 10, 0))
    mod_autils.patch_everywhere(
        monkeypatch,
        mod_autils.apathetic_testing,
        "get_sys_version_info",
        lambda: fake_sys.version_info,
        package_prefix=PROGRAM_PACKAGE,
        stitch_hints=PATCH_STITCH_HINTS,
    )
    # Verify the function works correctly (behavior, not implementation)
    result2 = mod_autils.fnmatchcase_portable("src/a/b/main.py", "src/**/main.py")
    assert result2 is True, "Function should work correctly for patterns with **"

    # --- verify ---
    # Verify behavior is correct (always checked above)
    # Implementation detail: patterns without ** should delegate to fnmatchcase
    assert fnmatchcase_calls_without_double_star > 0, (
        "Expected fnmatchcase to be called for patterns without **. "
        f"call_count={fnmatchcase_calls_without_double_star}"
    )


def test_fnmatchcase_portable_recursive_backport_python310(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """On Python 3.10, ** recursion is backported via custom regex."""
    # --- setup: force Python 3.10 ---
    fake_sys = SimpleNamespace(version_info=(3, 10, 0))
    mod_autils.patch_everywhere(
        monkeypatch,
        mod_autils.apathetic_testing,
        "get_sys_version_info",
        lambda: fake_sys.version_info,
        package_prefix=PROGRAM_PACKAGE,
        stitch_hints=PATCH_STITCH_HINTS,
    )

    # --- execute + verify ---
    # ** requires at least one path segment
    assert not mod_autils.fnmatchcase_portable("src/main.py", "src/**/main.py"), (
        "** requires at least one segment"
    )

    assert mod_autils.fnmatchcase_portable("src/a/b/c/main.py", "src/**/main.py")
    assert not mod_autils.fnmatchcase_portable("other/a/b/c/main.py", "src/**/main.py")


def test_fnmatchcase_portable_recursive_pattern_py310(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """fnmatchcase_portable() should use backport for ** patterns on Python 3.10."""
    # --- setup ---
    # Force Python 3.10
    fake_sys = SimpleNamespace(version_info=(3, 10, 0))
    mod_autils.patch_everywhere(
        monkeypatch,
        mod_autils.apathetic_testing,
        "get_sys_version_info",
        lambda: fake_sys.version_info,
        package_prefix=PROGRAM_PACKAGE,
        stitch_hints=PATCH_STITCH_HINTS,
    )

    # --- execute and verify ---
    # On Python 3.10, ** patterns should use backport
    # **/*.py should match files in subdirectories
    assert mod_autils.fnmatchcase_portable("src/utils/file.py", "src/**/*.py")
    assert mod_autils.fnmatchcase_portable("deep/nested/file.py", "**/*.py")
    # **/*.py requires at least one directory level
    assert not mod_autils.fnmatchcase_portable("src/file.py", "src/**/*.py")
    assert not mod_autils.fnmatchcase_portable("file.txt", "**/*.py")


def test_fnmatchcase_portable_edge_case_brackets_as_character_class() -> None:
    """Brackets create character classes in fnmatchcase."""
    # --- execute + verify ---
    # [1] is a character class, not a literal
    assert mod_autils.fnmatchcase_portable("file1.py", "file[1].py")
    assert not mod_autils.fnmatchcase_portable("file[1].py", "file[1].py")
    assert mod_autils.fnmatchcase_portable("file2.py", "file[1-9].py")


def test_fnmatchcase_portable_star_at_start() -> None:
    """* at start of pattern matches anything."""
    # --- execute + verify ---
    assert mod_autils.fnmatchcase_portable("main.py", "*.py")
    assert mod_autils.fnmatchcase_portable("test.py", "*.py")
    # * can cross / in fnmatchcase
    assert mod_autils.fnmatchcase_portable("src/main.py", "*.py")


def test_fnmatchcase_portable_double_star_at_start() -> None:
    """** at start requires at least one path component."""
    # --- execute + verify ---
    # ** requires at least one component
    assert not mod_autils.fnmatchcase_portable("file.py", "**/file.py")
    assert mod_autils.fnmatchcase_portable("src/file.py", "**/file.py")
    assert mod_autils.fnmatchcase_portable("src/a/b/file.py", "**/file.py")


def test_fnmatchcase_portable_double_star_at_end() -> None:
    """** at end matches any suffix."""
    # --- execute + verify ---
    assert mod_autils.fnmatchcase_portable("src/main.py", "src/**")
    assert mod_autils.fnmatchcase_portable("src/a/b/c/main.py", "src/**")
    assert not mod_autils.fnmatchcase_portable("other/main.py", "src/**")


def test_fnmatchcase_portable_complex_real_world_patterns() -> None:
    """Real-world complex patterns for gitignore-style matching."""
    # --- execute + verify ---
    # Python package with nested tests
    pattern = "src/**/test_*.py"
    assert mod_autils.fnmatchcase_portable("src/test/unit/test_main.py", pattern)
    # ** can match empty (zero-length)
    assert mod_autils.fnmatchcase_portable("src/test/test_main.py", pattern)
    assert not mod_autils.fnmatchcase_portable("src/main.py", "src/**/test_*.py")

    # Build artifact pattern
    # build/lib/main.py: ** matches 'lib/' (non-empty slash-separated)
    assert mod_autils.fnmatchcase_portable("build/lib/main.py", "build/**/*.py")
    assert mod_autils.fnmatchcase_portable("build/lib/a/b/c/main.py", "build/**/*.py")
    assert not mod_autils.fnmatchcase_portable("build/lib/main.txt", "build/**/*.py")

    # Ignore pattern (like .gitignore)
    # dist/bundle.js: first ** needs at least one component (doesn't match)
    assert not mod_autils.fnmatchcase_portable("dist/bundle.js", "**/dist/**")
    # app/dist/bundle.js: ** matches 'app/', then dist, then second ** matches 'sub/'
    assert mod_autils.fnmatchcase_portable("app/dist/bundle.js", "**/dist/**")
    assert mod_autils.fnmatchcase_portable(
        "app/nested/dist/sub/bundle.js", "**/dist/**"
    )


def test_fnmatchcase_portable_run_of_stars() -> None:
    """Consecutive stars (***+) treated as recursive **."""
    # --- execute + verify ---
    # For now, just test the behavior
    assert mod_autils.fnmatchcase_portable("src/a/b/c/main.py", "src**main.py")


def test_fnmatchcase_portable_special_chars_in_path() -> None:
    """Literal special chars in path (when not glob syntax)."""
    # --- execute + verify ---
    assert mod_autils.fnmatchcase_portable("file-1.py", "file-*.py")
    assert mod_autils.fnmatchcase_portable("file+1.py", "file+*.py")
    assert mod_autils.fnmatchcase_portable("file.1.py", "file.*.py")


@pytest.mark.skipif(sys.version_info < (3, 11), reason="Only relevant for Python 3.11+")
@pytest.mark.parametrize(
    ("path", "pattern"),
    [
        # Literal matches
        ("src/main.py", "src/main.py"),
        ("main.py", "other.py"),
        # Single star
        ("main.py", "*.py"),
        ("src/main.py", "*.py"),
        ("src/sub/main.py", "src/*.py"),
        # Double star
        ("src/main.py", "src/**/main.py"),
        ("src/a/main.py", "src/**/main.py"),
        ("src/a/b/c/main.py", "src/**/main.py"),
        ("test/main.py", "src/**/main.py"),
        # Question mark
        ("file1.py", "file?.py"),
        ("file12.py", "file?.py"),
        # Character class
        ("file1.py", "file[0-9].py"),
        ("fileA.py", "file[0-9].py"),
        # Complex patterns
        ("src/test/unit/test_main.py", "src/**/test_*.py"),
        ("build/lib/main.py", "build/**/*.py"),
        ("dist/bundle.js", "**/dist/**"),
        ("app/dist/bundle.js", "**/dist/**"),
    ],
)
def test_fnmatchcase_portable_matches_stdlib_on_py311_plus(
    path: str, pattern: str
) -> None:
    """On Python 3.11+, fnmatchcase_portable should match fnmatchcase behavior.

    This test verifies that our portable function doesn't diverge from the
    stdlib implementation on Python 3.11+, where fnmatchcase already supports **.
    """
    # --- execute + verify ---
    portable_result = mod_autils.fnmatchcase_portable(path, pattern)
    stdlib_result = fnmatchcase(path, pattern)
    assert portable_result == stdlib_result, (
        f"Mismatch for {path!r} vs {pattern!r}: "
        f"portable={portable_result}, stdlib={stdlib_result}"
    )
