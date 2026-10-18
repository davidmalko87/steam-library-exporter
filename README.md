# Steam Library Exporter

[![CI](https://github.com/davidmalko87/steam-library-exporter/actions/workflows/ci.yml/badge.svg)](https://github.com/davidmalko87/steam-library-exporter/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/steam-library-exporter.svg)](https://pypi.org/project/steam-library-exporter/)
[![PyPI downloads](https://img.shields.io/pypi/dm/steam-library-exporter.svg)](https://pypi.org/project/steam-library-exporter/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](https://github.com/davidmalko87/steam-library-exporter/blob/main/LICENSE)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
[![Last Commit](https://img.shields.io/github/last-commit/davidmalko87/steam-library-exporter)](https://github.com/davidmalko87/steam-library-exporter/commits/main)
[![Open Issues](https://img.shields.io/github/issues/davidmalko87/steam-library-exporter)](https://github.com/davidmalko87/steam-library-exporter/issues)

Export your full Steam game library to CSV or JSON with rich metadata from four APIs.

---

## Why?

Steam shows you your library — it doesn't let you query it.
This tool pulls playtime, genres, prices, reviews, Metacritic scores, community tags, and estimated ownership data into a single flat CSV you can open in Excel, pandas, Google Sheets, Tableau, or any BI tool.

---

## Features

| Feature | Description |
|---|---|
| Interactive mode | Run without arguments for a guided step-by-step setup — no flags to memorize |
| 24 metadata columns | appid, name, playtime, genres, developers, publishers, release date, Metacritic score, prices, review counts, SteamSpy tags, and more (20 with `--no-steamspy`) |
| CSV & JSON export | `--format csv` (default) or `--format json` for structured data |
| Four API sources | Steam Web API, Steam Store API, Steam Reviews API, SteamSpy |
| Sort options | `--sort playtime\|name\|metacritic\|reviews` |
| Filter unplayed | `--min-playtime N` to skip games under N hours |
| Environment variables | Set `STEAM_API_KEY` and `STEAM_ID` once — never retype credentials |
| Progress with ETA | Shows elapsed time and estimated time remaining per game |
| Export summary | Prints total playtime, played/unplayed counts, top genres, and avg Metacritic |
| Optional SteamSpy | Skip with `--no-steamspy` to cut export time by ~25% (drops the 4 SteamSpy columns) |
| Partial export | Use `--limit N` to test with a small batch before running the full library |
| Custom output path | Override the default filename with `--output` |
| Cross-platform | Runs on Windows, macOS, and Linux wherever Python 3.10+ is installed |

---

## Quick Start

### 1. Install

**Via PyPI (recommended)** — provides the `steam-export` command:

```bash
pip install steam-library-exporter
```

**Or as an isolated app with [pipx](https://pipx.pypa.io/)** — keeps its dependencies out of your global Python:

```bash
pipx install steam-library-exporter
```

**Upgrade:**

```bash
pip install -U steam-library-exporter              # pipx: pipx upgrade steam-library-exporter
```

**Or clone and run from source** (development):

```bash
git clone https://github.com/davidmalko87/steam-library-exporter.git
cd steam-library-exporter
python -m venv .venv
source .venv/bin/activate                          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python steam_export.py --help                      # same flags as steam-export
```

> **Where files live:** No config or `.env` file is read — credentials come only from `--key` / `--steamid` or the `STEAM_API_KEY` / `STEAM_ID` environment variables set in your shell. The export is written to the folder you run `steam-export` from as `steam_library.csv` (or `steam_library.json`) unless you pass `--output PATH`; nothing else is written, and progress goes to the terminal only. A clone behaves the same way.

### 2. Configure

You need two things:

| Item | How to get it |
|---|---|
| Steam Web API key | [steamcommunity.com/dev/apikey](https://steamcommunity.com/dev/apikey) (free) |
| Steam64 ID | [steamid.io](https://steamid.io) — 17-digit number |

Pass them with `--key` / `--steamid`, type them into interactive mode, or set them once as environment variables (see below).

> Set both **Profile** and **Game details** to **Public** in Steam → Settings → Privacy.

### 3. Run

```bash
steam-export --help        # all flags
steam-export               # interactive mode — guided step-by-step (no flags needed)
```

From a clone, use `python steam_export.py` in place of `steam-export` — the flags are identical. If `steam-export` is not on your PATH after a pip install, `python -m steam_export` runs the same CLI.

**CLI — export with flags:**

```bash
# Quick test — top 5 games by playtime
steam-export --key YOUR_API_KEY --steamid YOUR_STEAM64_ID --limit 5

# Full library export
steam-export --key YOUR_API_KEY --steamid YOUR_STEAM64_ID

# Export to JSON
steam-export --key YOUR_API_KEY --steamid YOUR_STEAM64_ID --format json

# Sort by name, skip unplayed games
steam-export --key YOUR_API_KEY --steamid YOUR_STEAM64_ID --sort name --min-playtime 1

# Faster — skip SteamSpy data (drops the 4 SteamSpy columns)
steam-export --key YOUR_API_KEY --steamid YOUR_STEAM64_ID --no-steamspy

# Custom output filename
steam-export --key YOUR_API_KEY --steamid YOUR_STEAM64_ID --output my_games.csv
```

**Environment variables — set once, then run without `--key` / `--steamid`:**

```bash
# macOS / Linux
export STEAM_API_KEY=YOUR_API_KEY
export STEAM_ID=YOUR_STEAM64_ID
steam-export --format csv
```

```powershell
# Windows (PowerShell)
$env:STEAM_API_KEY = "YOUR_API_KEY"
$env:STEAM_ID = "YOUR_STEAM64_ID"
steam-export --format csv
```

> Running `steam-export` with **no arguments** always starts interactive mode — the environment variables are only offered there as defaults (`Use this key? [Y/n]`). To export straight away (scripts, cron, Task Scheduler), pass at least one flag, as above.

---

## Configuration Reference

| Flag | Required | Default | Description |
|---|---|---|---|
| `--key KEY` | Yes* | — | Steam Web API key |
| `--steamid STEAMID` | Yes* | — | Steam64 ID (17-digit number) |
| `--output OUTPUT` | No | `steam_library.<format>` | Output file path |
| `--format FORMAT` | No | `csv` | Export format: `csv` or `json` |
| `--sort FIELD` | No | `playtime` | Sort by: `playtime`, `name`, `metacritic`, or `reviews` |
| `--min-playtime N` | No | `0` (all) | Minimum playtime in hours to include a game |
| `--no-steamspy` | No | off | Skip SteamSpy API calls (faster export; the 4 SteamSpy columns are omitted) |
| `--limit N` | No | `0` (all) | Export only the top N games by playtime |
| `--version` | No | — | Print version and exit |

*\* Not required if the corresponding environment variable is set.*

### Environment Variables

| Variable | Replaces |
|---|---|
| `STEAM_API_KEY` | `--key` |
| `STEAM_ID` | `--steamid` |

---

## Output Columns

`appid`, `name`, `playtime_hours`, `playtime_2weeks_hours`, `type`, `developers`, `publishers`, `genres`, `categories`, `release_date`, `metacritic_score`, `price_current`, `price_initial`, `is_free`, `short_description`, `header_image`, `total_positive`, `total_negative`, `review_score_desc`, `total_reviews`, `estimated_owners`, `avg_playtime_global`, `median_playtime_global`, `steamspy_tags`

- With `--no-steamspy` the last four (SteamSpy) columns are left out entirely, not blank, so the file has 20 columns.
- `playtime_hours` and `playtime_2weeks_hours` are your own playtime in hours; `avg_playtime_global` and `median_playtime_global` are SteamSpy figures in minutes.
- `price_current` and `price_initial` are Steam's formatted price strings (e.g. `$29.99`) in the currency Steam picks for your region; they are empty for free games.
- List fields (`developers`, `publishers`, `genres`, `categories`, `steamspy_tags`) are joined with `, `; `estimated_owners` is SteamSpy's range as returned (e.g. `20,000,000 .. 50,000,000`).
- Missing values are empty strings in both formats — JSON output uses `""`, not `null`.

### Sample rows

Selected columns, in export order:

```
appid,name,playtime_hours,genres,metacritic_score,price_current,review_score_desc,estimated_owners
570,Dota 2,1842.3,"Action, Strategy, Free To Play",90,,Very Positive,"100,000,000 .. 200,000,000"
730,Counter-Strike 2,634.1,"Action, Free To Play",,,Very Positive,"100,000,000 .. 200,000,000"
1091500,Cyberpunk 2077,112.7,RPG,86,$29.99,Very Positive,"20,000,000 .. 50,000,000"
```

---

## Project Structure

```
steam-library-exporter/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml
│   │   └── feature_request.yml
│   ├── workflows/
│   │   ├── ci.yml
│   │   └── publish.yml  # Publishes to PyPI when a v* tag is pushed
│   ├── dependabot.yml
│   └── PULL_REQUEST_TEMPLATE.md
├── steam_export.py      # CLI entry point and all logic
├── pyproject.toml       # Packaging metadata, steam-export console script
├── requirements.txt     # Python dependencies
├── CHANGELOG.md         # Version history
├── CONTRIBUTING.md      # Development and versioning guide
├── .gitignore
├── LICENSE              # MIT
└── README.md
```

---

## Known Limitations

- **Rate limits**: Steam Store API requires ~1.5 s between requests. A 200-game library takes roughly 13 minutes.
- **Private profiles**: The tool cannot read libraries set to Private in Steam Privacy Settings.
- **Free-to-play games**: Some F2P titles may lack price data in the Store API response.
- **SteamSpy accuracy**: Estimated ownership ranges are approximate (SteamSpy infers data, Steam does not publish it).
- **SteamSpy playtime**: SteamSpy currently returns `0` for average and median playtime, so `avg_playtime_global` and `median_playtime_global` are always `0`.
- **Excel and special characters**: The CSV is UTF-8 without a BOM. Double-clicking it in Excel on Windows can garble characters such as ™, ® or non-Latin titles; import it via **Data → From Text/CSV** with UTF-8 selected instead.
- **No incremental export**: The script always fetches and writes the full library from scratch.

---

## Security

> Never commit your API key. The `.gitignore` excludes common credential files (`.env`, `*.key`), but always verify before pushing.

Your Steam Web API key is read-only and scoped to public data, but treat it like any credential. On shared machines, prefer the environment variables over `--key`: command-line arguments are saved in your shell history and visible to other users in the process list.

---

## License

[MIT](https://github.com/davidmalko87/steam-library-exporter/blob/main/LICENSE) © 2026 David Malko

---

## Links

- [Changelog](https://github.com/davidmalko87/steam-library-exporter/blob/main/CHANGELOG.md)
- [Contributing guide](https://github.com/davidmalko87/steam-library-exporter/blob/main/CONTRIBUTING.md)
- [Open an issue](https://github.com/davidmalko87/steam-library-exporter/issues)
