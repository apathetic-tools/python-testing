# 🧩 Contributing Guide

Thanks for your interest in contributing to **Apathetic Python Testing** — a collection of utility functions for Apathetic Tools projects.

📚 **[Full Contributing Guide →](https://apathetic-tools.github.io/python-testing/contributing)**

For detailed information on setting up your environment, running checks, and contributing code, please visit our documentation website.

This file provides a quick reference for common development tasks.

---

## Quick Reference

### Development Commands

| Command | Description |
|----------|-------------|
| `poetry run poe check:fix` | Auto-fix issues, re-format, type-check, and re-test. |
| `poetry run poe check` | Run linting (`ruff`), type checks (`mypy`), and tests (`pytest`). |
| `poetry run poe fix` | Run all auto-fixers (`ruff`). |
| `poetry run poe build:stitched` | Bundle the project into a single portable script in `dist/`. |

### Setup

```bash
# Install dependencies
poetry install --with dev

# Run checks before committing
poetry run poe check:fix
```

---

## 🪶 Contribution Rules

- Follow [PEP 8](https://peps.python.org/pep-0008/) (enforced via Ruff).  
- Keep the **core library dependency-free** — dev tooling lives only in `pyproject.toml`'s `dev` group.  
- Run `poetry run poe check` before committing.  
- Open PRs against the **`main`** branch.  
- Be kind: small tools should have small egos.

---

**Thank you for helping keep Apathetic Python Testing minimal, dependency-free, and delightful.**
