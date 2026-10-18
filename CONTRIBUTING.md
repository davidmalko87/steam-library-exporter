# Contributing

Thank you for taking the time to contribute!

---

## Versioning policy

This project uses **[Semantic Versioning 2.0.0](https://semver.org/)** (`MAJOR.MINOR.PATCH`):

| Change type | Version bump | Example |
|---|---|---|
| Backwards-incompatible change (breaking API, removed flag, changed output schema) | **MAJOR** | `1.0.0` → `2.0.0` |
| New feature that is backwards-compatible (new flag, new column, new API source) | **MINOR** | `1.0.0` → `1.1.0` |
| Bug fix or internal improvement with no API/output change | **PATCH** | `1.0.0` → `1.0.1` |

---

## Version update rule

**Every commit that changes behaviour must update these three files together:**

1. `steam_export.py` — bump `__version__` to the new value.
2. `pyproject.toml` — set `version` under `[project]` to the same value (this is the version PyPI publishes).
3. `CHANGELOG.md` — add a new `## [X.Y.Z] — YYYY-MM-DD` section above the insertion-point comment.

Pull requests that change behaviour without updating all three files will not be merged.

### Changelog entry format

```markdown
## [X.Y.Z] — YYYY-MM-DD

### Added
- Short description of new features.

### Changed
- Short description of changed behaviour.

### Fixed
- Short description of bug fixes.

### Removed
- Short description of removed features.
```

Omit sections that don't apply.

---

## Development workflow

1. Fork the repository and create a branch: `git checkout -b feat/my-feature`.
2. Create a virtual environment and install the package in editable mode (this also provides the `steam-export` command):
   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Windows: .venv\Scripts\activate
   pip install -e .
   ```
3. Make changes and run the linter CI uses before committing:
   ```bash
   pip install ruff
   ruff check .
   ```
4. Bump the version in `steam_export.py` and `pyproject.toml` and add a `CHANGELOG.md` entry.
5. Push your branch and open a Pull Request against `main`.

---

## Releasing

Publishing to PyPI is automated by `.github/workflows/publish.yml`, which runs when a `v*` tag is pushed:

1. Merge the version bump (all three files above) into `main`.
2. Tag that commit with the same version and push the tag:
   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```
3. Check that the new version appears on [PyPI](https://pypi.org/project/steam-library-exporter/).

The tag must match `version` in `pyproject.toml`; PyPI rejects a version that has already been uploaded.

---

## Reporting issues

Please use the GitHub issue templates:

- **Bug report** — include your Python version, OS, and the exact error output.
- **Feature request** — describe the problem you are trying to solve.

---

## License

By contributing you agree that your contributions will be licensed under the [MIT License](LICENSE).
