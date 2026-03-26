"""
Steam Library Exporter
======================
Exports your Steam library with full metadata to CSV for analysis.

Pulls data from 3 sources:
  - Steam Web API (your library, playtime)
  - Steam Store API (genres, price, metacritic, description)
  - Steam Reviews API (positive/negative counts, score)
  - SteamSpy API (estimated owners, global playtime, tags)

Usage:
    python steam_export.py --key YOUR_API_KEY --steamid YOUR_STEAM64_ID
    python steam_export.py --key YOUR_API_KEY --steamid YOUR_STEAM64_ID --limit 5
    python steam_export.py --key YOUR_API_KEY --steamid YOUR_STEAM64_ID --no-steamspy

Get your API key:   https://steamcommunity.com/dev/apikey
Find your Steam64:  https://steamid.io
Privacy:            Set profile + game details to PUBLIC in Steam settings.
"""

import argparse
import csv
import sys
import time

import requests

__version__ = "1.0.0"

# --- Endpoints ---
OWNED_GAMES_URL = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
APP_DETAILS_URL = "https://store.steampowered.com/api/appdetails"
APP_REVIEWS_URL = "https://store.steampowered.com/appreviews/{appid}"
STEAMSPY_URL = "https://steamspy.com/api.php"

# --- Rate limit delays (seconds) ---
STORE_DELAY = 1.5
STEAMSPY_DELAY = 1.0


def get_owned_games(api_key: str, steam_id: str) -> list[dict]:
    """Fetch owned games list via Steam Web API."""
    params = {
        "key": api_key,
        "steamid": steam_id,
        "include_appinfo": 1,
        "include_played_free_games": 1,
        "format": "json",
    }
    resp = requests.get(OWNED_GAMES_URL, params=params, timeout=30)

    if resp.status_code != 200:
        print(f"[ERROR] GetOwnedGames returned HTTP {resp.status_code}")
        print(f"        Response: {resp.text[:500]}")
        sys.exit(1)

    data = resp.json().get("response", {})
    games = data.get("games", [])

    if not games:
        print("[WARNING] Got empty games list.")
        print("          Possible causes:")
        print("          - Profile or game details set to PRIVATE")
        print("          - Incorrect Steam64 ID (must be 17-digit number)")
        print("          - API key revoked or invalid")
        sys.exit(1)

    print(f"[OK] Found {len(games)} games in library.")
    return games


def get_store_details(appid: int) -> dict:
    """Fetch genre, price, metacritic, etc. from Steam Store API."""
    try:
        resp = requests.get(
            APP_DETAILS_URL,
            params={"appids": appid, "l": "english"},
            timeout=15,
        )
        if resp.status_code != 200:
            return {}
        result = resp.json()
        app_data = result.get(str(appid), {})
        if not app_data.get("success"):
            return {}
        return app_data.get("data", {})
    except Exception as e:
        print(f"  [WARN] Store API failed for {appid}: {e}")
        return {}


def get_review_summary(appid: int) -> dict:
    """Fetch review counts from Steam Reviews API."""
    try:
        resp = requests.get(
            APP_REVIEWS_URL.format(appid=appid),
            params={
                "json": 1,
                "language": "all",
                "purchase_type": "all",
                "num_per_page": 0,
            },
            timeout=15,
        )
        if resp.status_code != 200:
            return {}
        data = resp.json().get("query_summary", {})
        return {
            "total_positive": data.get("total_positive", ""),
            "total_negative": data.get("total_negative", ""),
            "review_score_desc": data.get("review_score_desc", ""),
            "total_reviews": data.get("total_reviews", ""),
        }
    except Exception:
        return {}


def get_steamspy_data(appid: int) -> dict:
    """Fetch estimated owners, avg playtime, tags from SteamSpy."""
    try:
        resp = requests.get(
            STEAMSPY_URL,
            params={"request": "appdetails", "appid": appid},
            timeout=15,
        )
        if resp.status_code != 200:
            return {}
        data = resp.json()
        tags = data.get("tags", {})
        tag_str = ", ".join(tags.keys()) if isinstance(tags, dict) else ""
        return {
            "estimated_owners": data.get("owners", ""),
            "avg_playtime_global": data.get("average_forever", ""),
            "median_playtime_global": data.get("median_forever", ""),
            "steamspy_tags": tag_str,
        }
    except Exception:
        return {}


def enrich_game(game: dict, use_steamspy: bool = True) -> dict:
    """Combine all sources into one flat row."""
    appid = game["appid"]
    name = game.get("name", f"Unknown ({appid})")
    playtime_hrs = round(game.get("playtime_forever", 0) / 60, 1)
    playtime_2wk = round(game.get("playtime_2weeks", 0) / 60, 1)

    row = {
        "appid": appid,
        "name": name,
        "playtime_hours": playtime_hrs,
        "playtime_2weeks_hours": playtime_2wk,
    }

    # --- Store details ---
    store = get_store_details(appid)
    if store:
        genres = store.get("genres", [])
        categories = store.get("categories", [])
        price_data = store.get("price_overview", {})

        row["type"] = store.get("type", "")
        row["developers"] = ", ".join(store.get("developers", []))
        row["publishers"] = ", ".join(store.get("publishers", []))
        row["genres"] = ", ".join(g["description"] for g in genres)
        row["categories"] = ", ".join(c["description"] for c in categories)
        row["release_date"] = store.get("release_date", {}).get("date", "")
        row["metacritic_score"] = store.get("metacritic", {}).get("score", "")
        row["price_current"] = price_data.get("final_formatted", "")
        row["price_initial"] = price_data.get("initial_formatted", "")
        row["is_free"] = store.get("is_free", "")
        row["short_description"] = store.get("short_description", "")
        row["header_image"] = store.get("header_image", "")
    else:
        for k in [
            "type", "developers", "publishers", "genres", "categories",
            "release_date", "metacritic_score", "price_current",
            "price_initial", "is_free", "short_description", "header_image",
        ]:
            row[k] = ""

    time.sleep(STORE_DELAY)

    # --- Reviews ---
    reviews = get_review_summary(appid)
    row["total_positive"] = reviews.get("total_positive", "")
    row["total_negative"] = reviews.get("total_negative", "")
    row["review_score_desc"] = reviews.get("review_score_desc", "")
    row["total_reviews"] = reviews.get("total_reviews", "")

    time.sleep(STORE_DELAY)

    # --- SteamSpy ---
    if use_steamspy:
        spy = get_steamspy_data(appid)
        row["estimated_owners"] = spy.get("estimated_owners", "")
        row["avg_playtime_global"] = spy.get("avg_playtime_global", "")
        row["median_playtime_global"] = spy.get("median_playtime_global", "")
        row["steamspy_tags"] = spy.get("steamspy_tags", "")
        time.sleep(STEAMSPY_DELAY)

    return row


def main():
    parser = argparse.ArgumentParser(description="Export Steam library to CSV")
    parser.add_argument("--key", required=True, help="Steam Web API key")
    parser.add_argument("--steamid", required=True, help="Steam64 ID (17 digits)")
    parser.add_argument("--output", default="steam_library.csv", help="Output CSV path")
    parser.add_argument("--no-steamspy", action="store_true", help="Skip SteamSpy (faster)")
    parser.add_argument("--limit", type=int, default=0, help="Limit games (0=all)")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(" Steam Library Exporter")
    print(f"{'='*60}\n")

    games = get_owned_games(args.key, args.steamid)
    games.sort(key=lambda g: g.get("playtime_forever", 0), reverse=True)

    if args.limit > 0:
        games = games[: args.limit]
        print(f"[INFO] Limited to top {args.limit} games by playtime.\n")

    rows = []
    total = len(games)
    for i, game in enumerate(games, 1):
        name = game.get("name", game["appid"])
        print(f"  [{i}/{total}] {name}...")
        row = enrich_game(game, use_steamspy=not args.no_steamspy)
        rows.append(row)

    if not rows:
        print("[ERROR] No data to write.")
        sys.exit(1)

    fieldnames = list(rows[0].keys())
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n[DONE] Exported {len(rows)} games -> {args.output}")
    print(f"       Columns: {', '.join(fieldnames)}")


if __name__ == "__main__":
    main()
