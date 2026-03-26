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
- [ ] `flake8 steam_export.py --max-line-length=100` passes with no errors
- [ ] `__version__` in `steam_export.py` bumped according to the [semver policy](CONTRIBUTING.md) (if behaviour changed)
- [ ] New entry added to `CHANGELOG.md` (if behaviour changed)
- [ ] README updated if new flags, columns, or usage patterns were introduced
