# Steam Library Exporter

[![CI](https://github.com/davidmalko87/steam-library-exporter/actions/workflows/ci.yml/badge.svg)](https://github.com/davidmalko87/steam-library-exporter/actions/workflows/ci.yml)
[![Version](https://img.shields.io/badge/version-1.1.0-blue)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)]()
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
| 24 metadata columns | appid, name, playtime, genres, developers, publishers, release date, Metacritic score, prices, review counts, SteamSpy tags, and more |
| CSV & JSON export | `--format csv` (default) or `--format json` for structured data |
| Four API sources | Steam Web API, Steam Store API, Steam Reviews API, SteamSpy |
| Sort options | `--sort playtime\|name\|metacritic\|reviews` |
| Filter unplayed | `--min-playtime N` to skip games under N hours |
| Environment variables | Set `STEAM_API_KEY` and `STEAM_ID` once — never retype credentials |
| Progress with ETA | Shows elapsed time and estimated time remaining per game |
| Export summary | Prints total playtime, played/unplayed counts, top genres, and avg Metacritic |
| Optional SteamSpy | Skip with `--no-steamspy` to cut export time by ~25% |
| Partial export | Use `--limit N` to test with a small batch before running the full library |
| Custom output path | Override the default filename with `--output` |
| Cross-platform | Runs on Windows, macOS, and Linux wherever Python 3.10+ is installed |

---

## Quick Start

### 1. Install

```bash
git clone https://github.com/davidmalko87/steam-library-exporter.git
cd steam-library-exporter
pip install -r requirements.txt
```

### 2. Configure

You need two things:

| Item | How to get it |
|---|---|
| Steam Web API key | [steamcommunity.com/dev/apikey](https://steamcommunity.com/dev/apikey) (free) |
| Steam64 ID | [steamid.io](https://steamid.io) — 17-digit number |

> Set both **Profile** and **Game details** to **Public** in Steam → Settings → Privacy.

### 3. Run

```bash
# Interactive mode — guided step-by-step (no flags needed)
python steam_export.py

# Quick test — top 5 games by playtime
python steam_export.py --key YOUR_API_KEY --steamid YOUR_STEAM64_ID --limit 5

# Full library export
python steam_export.py --key YOUR_API_KEY --steamid YOUR_STEAM64_ID

# Use environment variables (set once, run without --key / --steamid)
export STEAM_API_KEY=YOUR_API_KEY
export STEAM_ID=YOUR_STEAM64_ID
python steam_export.py

# Export to JSON
python steam_export.py --key YOUR_API_KEY --steamid YOUR_STEAM64_ID --format json

# Sort by name, skip unplayed games
python steam_export.py --key YOUR_API_KEY --steamid YOUR_STEAM64_ID --sort name --min-playtime 1

# Faster — skip SteamSpy data
python steam_export.py --key YOUR_API_KEY --steamid YOUR_STEAM64_ID --no-steamspy

# Custom output filename
python steam_export.py --key YOUR_API_KEY --steamid YOUR_STEAM64_ID --output my_games.csv
```

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
| `--no-steamspy` | No | off | Skip SteamSpy API calls (faster export) |
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

### Sample rows

```
appid,name,playtime_hours,metacritic_score,genres,price_current,review_score_desc,estimated_owners
570,Dota 2,1842.3,90,Action;Free to Play,0.0,Overwhelmingly Positive,100000000-200000000
730,Counter-Strike 2,634.1,83,Action,0.0,Very Positive,50000000-100000000
1091500,Cyberpunk 2077,112.7,86,Action;RPG,29.99,Very Positive,10000000-20000000
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
│   │   └── ci.yml
│   └── PULL_REQUEST_TEMPLATE.md
├── steam_export.py      # CLI entry point and all logic
├── requirements.txt     # Python dependencies
├── CHANGELOG.md         # Version history
├── CONTRIBUTING.md      # Development and versioning guide
├── LICENSE              # MIT
└── README.md
```

---

## Known Limitations

- **Rate limits**: Steam Store API requires ~1.5 s between requests. A 200-game library takes roughly 13 minutes.
- **Private profiles**: The tool cannot read libraries set to Private in Steam Privacy Settings.
- **Free-to-play games**: Some F2P titles may lack price data in the Store API response.
- **SteamSpy accuracy**: Estimated ownership ranges are approximate (SteamSpy infers data, Steam does not publish it).
- **No incremental export**: The script always fetches and writes the full library from scratch.

---

## Security

> Never commit your API key. The `.gitignore` excludes common credential files (`.env`, `*.key`), but always verify before pushing.

Your Steam Web API key is read-only and scoped to public data, but treat it like any credential.

---

## License

[MIT](LICENSE) © 2026 David Malko

---

## Links

- [Changelog](CHANGELOG.md)
- [Contributing guide](CONTRIBUTING.md)
- [Open an issue](https://github.com/davidmalko87/steam-library-exporter/issues)
