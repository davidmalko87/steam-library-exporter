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

## Two-file update rule

**Every commit that changes behaviour must update both files together:**

1. `steam_export.py` — bump `__version__` to the new value.
2. `CHANGELOG.md` — add a new `## [X.Y.Z] — YYYY-MM-DD` section above the insertion-point comment.

Pull requests that change behaviour without updating both files will not be merged.

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
2. Install dependencies: `pip install -r requirements.txt`.
3. Make changes and run the linter before committing:
   ```bash
   pip install flake8
   flake8 steam_export.py --max-line-length=100
   ```
4. Bump `__version__` in `steam_export.py` and add a `CHANGELOG.md` entry.
5. Push your branch and open a Pull Request against `main`.

---

## Reporting issues

Please use the GitHub issue templates:

- **Bug report** — include your Python version, OS, and the exact error output.
- **Feature request** — describe the problem you are trying to solve.

---

## License

By contributing you agree that your contributions will be licensed under the [MIT License](LICENSE).
