<!-- Roadmap.md -->
# 🧭 Roadmap

Some of these we just want to consider, and may not want to implement.

## 🎯 Core Features
- Logging fixtures for test isolation, TEST level debugging, and level change assertions ✅
- Safe patching (`patch_everywhere`) for all runtime modes (package, stitched, zipapp) ✅
- Runtime swap testing for validating stitched and zipapp builds ✅
- Mock superclass helpers for testing inheritance patterns ✅
- Grabbag utilities for common testing scenarios ✅

## 🧪 Tests
- Expand test coverage for edge cases in patch_everywhere
- Performance benchmarks for fixture setup/teardown
- Compatibility tests across Python 3.10+ versions

## 🧑‍💻 Development
- Stable phase: library is used in production by Apathetic Tools projects
- Identify and implement additional testing patterns as they emerge from real-world use

## 🔌 API
- Keep current fixtures and utilities stable
- Consider adding more specialized test helpers based on user feedback

## 📚 Documentation
- Expand API reference with more examples
- Add troubleshooting guide for common testing scenarios
- Document anti-patterns and best practices

## 🎯 Future: Pytest Plugins (Not Yet Implemented)
These are enhancements that would reduce boilerplate for users. Currently, users import fixtures directly from `apathetic_testing.logging`. In the future, we may implement these as automatic pytest plugins:

- **Automatic logging fixtures plugin** — Provide `isolated_logging`, `logging_test_level`, and `logging_level_testing` fixtures automatically without explicit imports
- **Runtime swap pytest plugin** — Enhanced `runtime_swap` with modified test reporting to show which runtime mode each test ran against
- **True quiet mode** — Minimal test output mode with only essential information (pass/fail counts, errors)
- **Incremental caching for tests** — Cache test results across runs and only re-run tests when code or dependencies change

These would integrate seamlessly with pytest's plugin infrastructure and reduce setup requirements for new projects. Implementation would focus on:
- Auto-registration of fixtures via `pytest_plugins` hook
- Pytest reporting hooks for enhanced output
- Cache persistence and invalidation logic


> See [REJECTED.md](REJECTED.md) for experiments and ideas that were explored but intentionally not pursued.

---

> ✨ *AI was used to help draft language, formatting, and code — plus we just love em dashes.*

<p align="center">
  <sub>😐 <a href="https://apathetic-tools.github.io/">Apathetic Tools</a> © <a href="./LICENSE">MIT-a-NOAI</a></sub>
</p>
