## Summary

<!-- Describe what this PR does and why. -->

---

## Type of change

- [ ] Bug fix (PATCH bump — no API or output format changes)
- [ ] New feature (MINOR bump — backwards-compatible)
- [ ] Breaking change (MAJOR bump — changes CLI flags or output columns)
- [ ] Refactor (no behaviour change, no version bump needed)
- [ ] Documentation only

---

## Checklist

- [ ] Tested locally with a real Steam API key and Steam64 ID (or `--limit 5` for a quick run)
- [ ] `ruff check .` passes with no errors (same check as CI)
- [ ] `__version__` in `steam_export.py` and `version` in `pyproject.toml` bumped according to the [semver policy](https://github.com/davidmalko87/steam-library-exporter/blob/main/CONTRIBUTING.md#versioning-policy) (if behaviour changed)
- [ ] New entry added to `CHANGELOG.md` (if behaviour changed)
- [ ] README updated if new flags, columns, or usage patterns were introduced
