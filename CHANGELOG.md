# CHANGELOG

<!-- version list -->

## v0.3.0 (2026-01-01)

### Features

- **mock**: Add create_mock_version_info for testing version checks
  ([`30602e5`](https://github.com/apathetic-tools/python-testing/commit/30602e5a68c2ec109b485c4bcdd0a44a1bbc88e7))

- **types**: Add __init__.pyi stub to export nested classes for mypy
  ([`b1fcf0b`](https://github.com/apathetic-tools/python-testing/commit/b1fcf0b47c396125dda24083be41c3b2de45b543))


## v0.2.1 (2025-12-31)

### Bug Fixes

- **pyproject**: Add pytest plugin packages to poetry config
  ([`4acf2d6`](https://github.com/apathetic-tools/python-testing/commit/4acf2d65bf8a5e558ade3f5906292d03739104ee))


## v0.2.0 (2025-12-30)

### Documentation

- Add pytest plugin opt-out guide
  ([`fe14617`](https://github.com/apathetic-tools/python-testing/commit/fe14617252bf1a30a49c5d39bfd8b647c73143d9))

### Features

- Add has_pytest_plugin_enabled() utility for plugin detection
  ([`71235e7`](https://github.com/apathetic-tools/python-testing/commit/71235e710be95546b41bee01b1bf2f7c38f860c7))

- Add pytest_timeout_defaults and pytest_xdist_quiet plugins
  ([`59147ed`](https://github.com/apathetic-tools/python-testing/commit/59147ed0bcc853dd456db7e23dd2ac7d25dac309))

### Refactoring

- **pytest_timeout_defaults**: Simplify plugin by removing defensive checks
  ([`fd6ed49`](https://github.com/apathetic-tools/python-testing/commit/fd6ed494cfbbe6b0758f82af7a9d2e7afb9b2663))

- **tests**: Rename tests/30_independant to tests/30_unit
  ([`6307d26`](https://github.com/apathetic-tools/python-testing/commit/6307d26c99ddfd0a9b0341cc18fe7c418a249263))

- **tests**: Split unit tests into individual files per function
  ([`3a8ea80`](https://github.com/apathetic-tools/python-testing/commit/3a8ea8066324b6fcfc5b4abddf2299cbadff25c0))


## v0.1.0 (2025-12-30)

- Initial Release
