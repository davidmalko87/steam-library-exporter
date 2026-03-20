# Steam Library Exporter — Export Steam Games Data to CSV (Python)

Python CLI tool to **export your full Steam game library** to a CSV file with rich metadata — playtime hours, genres, user reviews, Metacritic scores, prices, community tags, and estimated ownership data.

Built for gamers and data enthusiasts who want to **analyze their Steam library**, explore gaming habits, compare games, or build dashboards from real Steam data.

## What Data Gets Exported

Combines **3 free APIs** into a single flat CSV with 24 columns:

| Source | Exported Fields |
|--------|----------------|
| **Steam Web API** | your total playtime (hours), playtime last 2 weeks |
| **Steam Store API** | genres, categories, developers, publishers, release date, Metacritic score, current & original price, free-to-play flag, game description, header image URL |
| **Steam Reviews API** | total positive reviews, total negative reviews, review score description, total review count |
| **SteamSpy API** | estimated owners, global average playtime, global median playtime, community tags |

## Prerequisites

1. **Python 3.10+** with `requests` installed
2. **Steam Web API key** — get one free at https://steamcommunity.com/dev/apikey
3. **Your Steam64 ID** (17-digit number) — find it at https://steamid.io
4. **Public Steam profile** — set both profile AND game details to Public in [Steam Privacy Settings](https://steamcommunity.com/my/edit/settings)

## Installation

```bash
git clone https://github.com/davidmalko87/steam-library-exporter.git
cd steam-library-exporter
pip install -r requirements.txt
```

## Usage

```bash
# Quick test — export top 5 games by playtime
python steam_export.py --key YOUR_API_KEY --steamid YOUR_STEAM64_ID --limit 5

# Full library export to CSV
python steam_export.py --key YOUR_API_KEY --steamid YOUR_STEAM64_ID

# Faster export — skip SteamSpy data
python steam_export.py --key YOUR_API_KEY --steamid YOUR_STEAM64_ID --no-steamspy

# Custom output filename
python steam_export.py --key YOUR_API_KEY --steamid YOUR_STEAM64_ID --output my_games.csv
```

## Output Format

Creates `steam_library.csv` (default) with these columns:

```
appid, name, playtime_hours, playtime_2weeks_hours, type, developers,
publishers, genres, categories, release_date, metacritic_score,
price_current, price_initial, is_free, short_description, header_image,
total_positive, total_negative, review_score_desc, total_reviews,
estimated_owners, avg_playtime_global, median_playtime_global, steamspy_tags
```

Games are sorted by your playtime (most played first).

## Rate Limits & Performance

- Steam Store API is rate-limited — the script adds 1.5s delay between requests
- SteamSpy adds 1.0s delay per game
- **~4 seconds per game** — a 200-game library takes ~13 minutes
- Use `--limit N` to test with a small batch first
- Use `--no-steamspy` to cut export time by ~25%

## Use Cases

- **Analyze your gaming habits** — find your most played genres, total hours invested
- **Compare game reviews** — filter by Metacritic score, positive review ratio
- **Track your backlog** — find unplayed games (0 hours) you own
- **Price analysis** — see how much you spent vs. current prices
- **Data visualization** — import CSV into pandas, Google Sheets, Tableau, Power BI

## Security

⚠️ **Never commit your API key.** The `.gitignore` excludes common sensitive files, but always verify before pushing.

Your Steam Web API key is read-only and scoped to public data, but treat it like a credential.

## License

MIT
