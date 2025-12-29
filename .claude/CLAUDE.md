# Communication

### Asking Questions

When asking questions, **wait for response** before proceeding. Exception: direct instructions (e.g., "add a function") are confirmation.

### Handling Developer Questions

If developer asks ANY question (including "do we need X?", "can we Y?"), you **must**:
1. Answer completely with recommendations
2. Ask what to do and **stop** - no implementation
3. Wait for response

Exploratory work (reading/searching) is allowed; no code changes.

### Troubleshooting When Stuck

Ask user for insight. Also ask if you should: stash changes, rollback, or add isolated changes one at a time. If yes, create plan in `.plan/` per `.ai/templates/plan_debug_rollback.tmpl.md` and consult `.ai/workflows/plan_debug_rollback.md`.

### Using Plan Documents

For complex features, refactors, API changes, or multi-phase work, use the plan format (`.ai/workflows/plan_feature.md`). Plans help coordinate work, track progress, and ensure all phases are completed.

# Git Conventions

### Git Commit Conventions
- No AI tool attribution or Co-Authored-By trailers
- Format: `type(scope): subject`
- See `.ai/workflows/commit.md` for details

### Checkpoint Commits and Squashing

**Checkpoint format**: `checkpoint(scope): brief description` (intermediate saves during debugging)

**Before regular commit**: Check for checkpoint commits since last regular commit using:
```bash
LAST_REGULAR=$(git log --format="%H|%s" | awk -F'|' '$2 !~ /^checkpoint\(/ {print $1; exit}')
git log --format="%H|%s" ${LAST_REGULAR}..HEAD | awk -F'|' '$2 ~ /^checkpoint\(/ {print $1, $2}'
```
This finds the last commit that is NOT a checkpoint (subject doesn't start with "checkpoint("), then checks for checkpoint commits between that and HEAD. If checkpoint commits are found, ask: "I see [N] checkpoint commit(s). Squash with this commit?" and wait for response. If yes, squash via rebase/reset; if no, proceed.

**Important**: The check must examine the subject line only (not the commit message body), as commits may mention "checkpoint" in the body without being checkpoint commits.

# Project Overview

## Apathetic Python Testing Project Context

Collection of utility functions for Apathetic Tools projects. Lightweight, dependency-free, for CLI tools.

See: `pyproject.toml` (configs/tasks), `ROADMAP.md` (roadmap)

# Project Structure

### Important Files
- `dist/apathetic_testing.py` is **generated** - never edit. Generate via `poetry run poe build:script`
- `dist/` contains build outputs - do not edit

### Project Structure
- `src/package_name/` - Main source code
- `tests/` - Test suite
- `dev/` - Development scripts (**NEVER edit** - report problems, don't fix)

# Pytest Structure

### PyTest Structure

## Packages
- Only `tests/` and `tests/utils/` should have `__init__.py`. Do NOT add `__init__.py` to test subdirectories (e.g., `tests/0_tooling/`, `tests/3_independant/`, `tests/5_core/`, etc.). Test subdirectories are not Python packages.
- Use `tests/utils/` to colocate utilities that are generally helpful for tests or used in multiple test files.

## Imports
- Never import from one test_* file into another test_* file.
- Never use `from <package> import <func>` for any `src/` packages, instead use `import <package> as mod_<package>` then use `mod_<package>.<func>`
- Don't import general utilities not under test from `src/` as test setup helpers. You may call related src functions in a test even if they are not primarily under test. Use `tests/utils/`as helpers only even if you have to replicate the src utility.
- You can import constants from `src/` code to use in tests, follow import rules.
- When writting new tests, be aware of our test utilities in `tests/utils/`, especially `patch_everywhere`

## Directories
- Integration tests go in their own directories separate from unit tests.

## Files
- Unit tests should have a single file per function tested.
- Integration tests should have a single file per feature or topic.
- Tests primarily testing private functions go in their own file `test_priv__<function name no leading underscore>.py` with a file level ignore statement.
- Tests primarily acting as a lint rule go in their own file  `test_lint__<purpose>.py` and should not be modified as a means of ignoring the failure. Fix the error reported instead.

## Runtime
- Tests run with `test` log-level by default so trace and debug statements bypass capsys and go to __stderr__.
- Tests are usually run twice, once against the `src/` directory, and again using our `tests/utils/runtime_swap.py` against the `dist/<package>.py` stitched file.

# Python Code Quality

# Python Code Quality

Does not apply to generated or externally sourced code `dist/`, `bin/`.


## Line Length

Max 88 chars (Ruff enforced). **Always fix violations; never ignore.**

**Principle**: Prioritize readability over meeting the limit.

**Comments/Strings**: Don't shorten if it hurts readability. Split across lines instead:
```python
# Validate user input before processing to ensure data integrity
# and prevent security vulnerabilities.

error_message = (
    "Failed to validate user input. Please check the format "
    "and ensure all required fields are present."
)
```

**Inline statements** (ternaries, comprehensions, generators): Wrap across lines or refactor to explicit if/else/loops for complex cases.

## Python Version

**Minimum**: Python 3.10. All code must work on 3.10.

**Newer features**: Use 3.11+ features if supported on both versions via:
- `from __future__` imports
- `typing_extensions`
- Backported implementations

**Backporting**: Encapsulate version differences in functions. Document clearly. Examples: `fnmatch_portable()`, `load_toml()`. Limit: ~few hundred lines max. If too large/complex, ask developer.

### Checks and Tests

**Requirement**: `poetry run poe check:fix` must pass completely before finishing work. Runs: formatting, linting, type checking, tests (both installed and singlefile runtimes). **CI blocks pushes until this passes.**

**Commands**: `poetry run poe check:fix` (main), `check`, `fix`, `lint`, `typecheck`, `test`. Individual: `lint:ruff`, `fix:ruff:installed`, `fix:format:installed`, `typecheck:mypy`, `typecheck:pyright`, `test:pytest:installed`, `test:pytest:script`.

**Single files**: `ruff format/check/check --fix <file>`, `pytest <file>::<test>` (add `RUNTIME_MODE=singlefile` for singlefile mode).

# Type Checking

### Type Checking and Linting Best Practices

**Fix over ignore**: Always fix when possible. Use ignore comments only for: signature-matching requirements (pytest hooks, interfaces), defensive checks with value, or two tools that conflict.

**Ignore comments**: End of line, don't count toward line length. Examples: `# type: ignore[error-code]`, `# pyright: ignore[error-code]`, `# noqa: CODE`

**Common patterns**:
- Unused args: Prefix with `_` unless signature must match (pytest hooks, interfaces) - then ignore
- Complexity/param warnings: Refactor if improves readability; otherwise ignore
- Type inference: Use `cast_hint()` (project utils) or `typing.cast()` (not in tests). `cast_hint()` for intentional narrowing/IDE inference; `cast()` for Union/Optional/nested generics
- Defensive checks: `isinstance()` with ignore only for external data (params, config, user input). Not for constants.

**TypedDict maintenance**: Always update TypedDict when adding properties. Add `_new_field: NotRequired[Type]` (or `Type` if required). Never use `type: ignore` to bypass missing fields.

**Resolved TypedDict pattern**: "Resolved" TypedDicts (e.g., `ConfigResolved`) - fields that can be resolved (even to empty defaults) should always be present, not `NotRequired`. Use `NotRequired` only for truly optional fields that may never be set. Examples: ✅ `items: list[Item]` (resolves to `[]`), ✅ `optional_feature: NotRequired[str]` (conditional), ❌ `items: NotRequired[list[Item]]` (can resolve to `[]`).

**Configuration files**: NEVER modify `pyproject.toml`, `pytest.ini`, or tool configs to "fix" errors. STOP and ask developer if needed. Exception: explicit user request.

# Workflow

### Execution and Workflow
- **VENV:** Use the poetry venv for execution, e.g. `poetry run python3` (not bare `python3`)
- **Poe tasks**: `check`, `fix`, `test`, `coverage`, `check:fix` (before commit), `build:script`
- **NEVER edit `.cursor/` or `.claude/` directly**: Generated from `.ai/`. Edit `.ai/rules/` or `.ai/commands/`, then run `poetry run poe sync:ai:guidance` and include generated files in commit.
- **Before committing**: Run `poetry run poe check:fix`
- **Debugging tests**: 
  1. First try `LOG_LEVEL=test poetry run poe test:pytest:installed tests/path/to/test.py::test_name -xvs`. 
  2. If stuck, see `.ai/workflows/debug_tests.md`

### Plan File Management

When creating a **new** plan document:
- Check `.plan/` for plan files older than 24 hours
- If found, ask developer if they should be deleted
- Note any plans that are not marked as all phases completed
- Keep implemented/completed plans; only ask about stale incomplete plans

### When to Read Workflow/Template Files

Only read `.ai/workflows/` or `.ai/templates/` when: condition is met (e.g., stuck debugging → read `debug_tests.md`), or directly asked to work on them. Mentions in rules are references, not immediate read instructions.

# Claude Extra

## AI Model Strategy

When identifying tasks that require complex reasoning, planning, or analysis, ask for confirmation before proceeding:

> "This task appears to require significant planning and reasoning. Would you like me to use a hybrid model approach to create a detailed execution plan first, then switch to a faster model for implementation?"

If confirmed, follow this workflow:
1. **Check model availability**: Determine if the Opus model is available for the Task tool
2. **Planning phase**: 
   - If Claude Opus is available: Use the Task tool with `model: "opus"` and `subagent_type: "general-purpose"` to create a detailed execution plan and document the approach
   - If Claude Opus is not available: Use the Task tool with `model: "sonnet"` and `subagent_type: "general-purpose"` to create a detailed execution plan and document the approach
3. **Execution phase**: After receiving the plan:
   - If Opus was used for planning: Use Claude Sonnet to implement the plan following the documented steps
   - If Sonnet was used for planning: Use Claude Haiku to implement the plan following the documented steps

This hybrid approach combines the most capable model's superior reasoning for complex problems with faster models' speed for straightforward implementation.


