# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — 2026-03-26

### Added
- `steam_export.py`: CLI tool to export a Steam library to CSV with 24 columns of metadata.
- Pulls data from four APIs: Steam Web API, Steam Store API, Steam Reviews API, and SteamSpy.
- `--key`, `--steamid`, `--output`, `--limit`, and `--no-steamspy` CLI flags.
- Rate-limiting delays (1.5 s / Store, 1.0 s / SteamSpy) to respect upstream limits.
- `requirements.txt` pinning `requests>=2.28.0`.
- `.gitignore` covering common Python artefacts and sensitive credential files.
- `LICENSE` (MIT, © 2026 David Malko).
- `README.md` with badges, usage examples, output column reference, and performance notes.
- `__version__` constant (`1.0.0`) in `steam_export.py`.

---

<!-- insertion point — add new entries above this line -->
