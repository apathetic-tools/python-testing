<!-- Roadmap.md -->
# 🧭 Roadmap

Some of these we just want to consider, and may not want to implement.

## 🎯 Core Features
- None currently planned.

## 🧪 Tests
- Expand test coverage for edge cases in patch_everywhere
- Performance benchmarks for fixture setup/teardown
- Identify and implement additional testing patterns as they emerge from real-world use

## 🧑‍💻 Development
- Stable phase: library is used in production by Apathetic Tools projects

## 🔌 API


## 📚 Documentation
- Add troubleshooting guide for common testing scenarios
- Document anti-patterns and best practices

## 🎯 Future: Pytest Plugins (Not Yet Implemented)
These are enhancements that would reduce boilerplate for users. Currently, users import fixtures directly from `apathetic_testing.logging`. In the future, we may implement these as automatic pytest plugins:

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
