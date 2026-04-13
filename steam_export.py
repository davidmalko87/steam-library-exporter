"""
Steam Library Exporter
======================
Exports your Steam library with full metadata to CSV or JSON for analysis.

Pulls data from 4 sources:
  - Steam Web API (your library, playtime)
  - Steam Store API (genres, price, metacritic, description)
  - Steam Reviews API (positive/negative counts, score)
  - SteamSpy API (estimated owners, global playtime, tags)

Usage:
    python steam_export.py                               # Interactive mode
    python steam_export.py --key KEY --steamid ID        # CLI mode (CSV)
    python steam_export.py --key KEY --steamid ID --format json
    python steam_export.py --key KEY --steamid ID --sort name --min-playtime 1

Environment variables:
    STEAM_API_KEY   Your Steam Web API key
    STEAM_ID        Your Steam64 ID

Get your API key:   https://steamcommunity.com/dev/apikey
Find your Steam64:  https://steamid.io
Privacy:            Set profile + game details to PUBLIC in Steam settings.
"""

import argparse
import csv
import json
import os
import sys
import time

import requests

__version__ = "1.1.0"

# --- Endpoints ---
OWNED_GAMES_URL = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
APP_DETAILS_URL = "https://store.steampowered.com/api/appdetails"
APP_REVIEWS_URL = "https://store.steampowered.com/appreviews/{appid}"
STEAMSPY_URL = "https://steamspy.com/api.php"

# --- Rate limit delays (seconds) ---
STORE_DELAY = 1.5
STEAMSPY_DELAY = 1.0

# --- Sort keys ---
SORT_OPTIONS = {
    "playtime": "playtime_hours",
    "name": "name",
    "metacritic": "metacritic_score",
    "reviews": "total_reviews",
}


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


# ── Helpers ──────────────────────────────────────────────────────────


def format_duration(seconds: float) -> str:
    """Format seconds into a human-readable duration string."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    if minutes < 60:
        return f"{minutes}m {secs:02d}s"
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours}h {mins:02d}m"


def export_rows(rows: list[dict], output: str, fmt: str):
    """Write rows to the specified output format."""
    if fmt == "json":
        with open(output, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2, ensure_ascii=False)
    else:
        fieldnames = list(rows[0].keys())
        with open(output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)


def sort_rows(rows: list[dict], sort_key: str) -> list[dict]:
    """Sort enriched rows by the given key."""
    field = SORT_OPTIONS.get(sort_key, "playtime_hours")
    reverse = sort_key != "name"

    def sort_val(row):
        val = row.get(field, "")
        if val == "":
            return -1 if reverse else ""
        return val

    return sorted(rows, key=sort_val, reverse=reverse)


def print_summary(rows: list[dict]):
    """Print summary statistics after export."""
    total_playtime = sum(r.get("playtime_hours", 0) for r in rows)
    played = [r for r in rows if r.get("playtime_hours", 0) > 0]
    unplayed = len(rows) - len(played)

    genre_counts: dict[str, int] = {}
    for r in rows:
        for g in str(r.get("genres", "")).split(", "):
            g = g.strip()
            if g:
                genre_counts[g] = genre_counts.get(g, 0) + 1
    top_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    scores = [
        r["metacritic_score"] for r in rows
        if isinstance(r.get("metacritic_score"), (int, float))
        and r["metacritic_score"] != ""
    ]
    avg_meta = round(sum(scores) / len(scores), 1) if scores else "N/A"

    print(f"\n{'─' * 50}")
    print(" Export Summary")
    print(f"{'─' * 50}")
    print(f"  Total games exported : {len(rows)}")
    print(f"  Played               : {len(played)}")
    print(f"  Unplayed             : {unplayed}")
    print(f"  Total playtime       : {total_playtime:,.1f} hours")
    if played:
        print(f"  Avg playtime (played): {total_playtime / len(played):,.1f} hours")
    print(f"  Avg Metacritic score : {avg_meta}")
    if top_genres:
        genre_str = ", ".join(f"{g} ({c})" for g, c in top_genres)
        print(f"  Top genres           : {genre_str}")
    print(f"{'─' * 50}")


# ── Interactive mode ─────────────────────────────────────────────────


def prompt_choice(prompt: str, options: list[str], default: str) -> str:
    """Prompt the user to pick from a list of options."""
    while True:
        val = input(f"  {prompt} [{'/'.join(options)}] ({default}): ").strip().lower()
        if not val:
            return default
        if val in options:
            return val
        print(f"    Invalid choice. Options: {', '.join(options)}")


def prompt_int(prompt: str, default: int) -> int:
    """Prompt the user for an integer."""
    while True:
        val = input(f"  {prompt} ({default}): ").strip()
        if not val:
            return default
        try:
            return int(val)
        except ValueError:
            print("    Please enter a number.")


def prompt_string(prompt: str, default: str = "", required: bool = False) -> str:
    """Prompt the user for a string value."""
    suffix = f" ({default})" if default else ""
    while True:
        val = input(f"  {prompt}{suffix}: ").strip()
        if not val and default:
            return default
        if not val and required:
            print("    This field is required.")
            continue
        if val:
            return val
        return default


def interactive_mode() -> dict:
    """Run the interactive menu when no CLI args are provided."""
    print(f"\n{'=' * 55}")
    print(f"  Steam Library Exporter v{__version__} — Interactive Mode")
    print(f"{'=' * 55}")
    print()
    print("  No arguments detected. Starting guided setup.")
    print("  (Tip: run with --help to see CLI flags)")
    print()

    # --- Credentials ---
    env_key = os.environ.get("STEAM_API_KEY", "")
    env_id = os.environ.get("STEAM_ID", "")

    print("─── Credentials ───────────────────────────────────")
    if env_key:
        masked = env_key[:4] + "****" + env_key[-4:]
        print(f"  Found STEAM_API_KEY in environment: {masked}")
        use_env = input("  Use this key? [Y/n]: ").strip().lower()
        api_key = env_key if use_env != "n" else prompt_string("Steam API Key", required=True)
    else:
        print("  Get your key at: https://steamcommunity.com/dev/apikey")
        api_key = prompt_string("Steam API Key", required=True)

    print()
    if env_id:
        print(f"  Found STEAM_ID in environment: {env_id}")
        use_env = input("  Use this ID? [Y/n]: ").strip().lower()
        steam_id = env_id if use_env != "n" else prompt_string("Steam64 ID", required=True)
    else:
        print("  Find yours at: https://steamid.io")
        steam_id = prompt_string("Steam64 ID (17-digit number)", required=True)

    # --- Export Options ---
    print()
    print("─── Export Options ────────────────────────────────")
    fmt = prompt_choice("Export format", ["csv", "json"], "csv")
    sort_by = prompt_choice(
        "Sort by", ["playtime", "name", "metacritic", "reviews"], "playtime",
    )
    min_playtime = prompt_int("Min playtime in hours (0 = include all)", 0)
    limit = prompt_int("Limit to top N games (0 = all)", 0)
    use_steamspy = prompt_choice("Include SteamSpy data?", ["y", "n"], "y") == "y"

    default_output = f"steam_library.{fmt}"
    output = prompt_string("Output filename", default=default_output)

    # --- Confirm ---
    print()
    print("─── Review ────────────────────────────────────────")
    print(f"  Format      : {fmt.upper()}")
    print(f"  Sort        : {sort_by}")
    if min_playtime:
        print(f"  Min playtime: {min_playtime}h")
    else:
        print("  Min playtime: all games")
    if limit:
        print(f"  Limit       : top {limit}")
    else:
        print("  Limit       : all games")
    print(f"  SteamSpy    : {'yes' if use_steamspy else 'no'}")
    print(f"  Output      : {output}")
    print()

    confirm = input("  Proceed? [Y/n]: ").strip().lower()
    if confirm == "n":
        print("\n  Export cancelled.")
        sys.exit(0)

    return {
        "key": api_key,
        "steamid": steam_id,
        "output": output,
        "format": fmt,
        "sort": sort_by,
        "min_playtime": min_playtime,
        "limit": limit,
        "no_steamspy": not use_steamspy,
    }


# ── Export pipeline ──────────────────────────────────────────────────


def run_export(cfg: dict):
    """Run the export pipeline with the given configuration."""
    print(f"\n{'=' * 55}")
    print(" Steam Library Exporter")
    print(f"{'=' * 55}\n")

    games = get_owned_games(cfg["key"], cfg["steamid"])
    games.sort(key=lambda g: g.get("playtime_forever", 0), reverse=True)

    if cfg["limit"] > 0:
        games = games[: cfg["limit"]]
        print(f"[INFO] Limited to top {cfg['limit']} games by playtime.\n")

    if cfg["min_playtime"] > 0:
        before = len(games)
        min_mins = cfg["min_playtime"] * 60
        games = [g for g in games if g.get("playtime_forever", 0) >= min_mins]
        skipped = before - len(games)
        print(
            f"[INFO] Filtered to {len(games)} games with >= {cfg['min_playtime']}h "
            f"playtime (removed {skipped}).\n"
        )

    rows: list[dict] = []
    total = len(games)
    export_start = time.time()

    for i, game in enumerate(games, 1):
        name = game.get("name", game["appid"])
        elapsed = time.time() - export_start
        if i > 1:
            avg_per_game = elapsed / (i - 1)
            remaining = avg_per_game * (total - i + 1)
            eta_str = f" | elapsed {format_duration(elapsed)}, ETA ~{format_duration(remaining)}"
        else:
            eta_str = ""
        print(f"  [{i}/{total}] {name}...{eta_str}")
        row = enrich_game(game, use_steamspy=not cfg["no_steamspy"])
        rows.append(row)

    if not rows:
        print("[ERROR] No data to write.")
        sys.exit(1)

    # Re-sort after enrichment when sorting by metadata fields
    sort_key = cfg.get("sort", "playtime")
    if sort_key != "playtime":
        rows = sort_rows(rows, sort_key)

    fmt = cfg.get("format", "csv")
    output = cfg["output"]
    export_rows(rows, output, fmt)

    total_time = time.time() - export_start
    print(f"\n[DONE] Exported {len(rows)} games -> {output} ({format_duration(total_time)})")

    if fmt == "csv":
        fieldnames = list(rows[0].keys())
        print(f"       Columns: {', '.join(fieldnames)}")

    print_summary(rows)


# ── CLI entry point ──────────────────────────────────────────────────


def main():
    # Interactive mode when run with no arguments
    if len(sys.argv) == 1:
        cfg = interactive_mode()
        run_export(cfg)
        return

    parser = argparse.ArgumentParser(
        description="Export Steam library to CSV or JSON",
        epilog="Run without arguments for interactive mode. "
               "Set STEAM_API_KEY / STEAM_ID env vars to skip typing credentials.",
    )
    parser.add_argument(
        "--key",
        default=os.environ.get("STEAM_API_KEY", ""),
        help="Steam Web API key (or set STEAM_API_KEY env var)",
    )
    parser.add_argument(
        "--steamid",
        default=os.environ.get("STEAM_ID", ""),
        help="Steam64 ID (or set STEAM_ID env var)",
    )
    parser.add_argument(
        "--output", default="",
        help="Output file path (default: steam_library.<format>)",
    )
    parser.add_argument(
        "--format", choices=["csv", "json"], default="csv",
        help="Export format (default: csv)",
    )
    parser.add_argument(
        "--sort", choices=["playtime", "name", "metacritic", "reviews"],
        default="playtime",
        help="Sort order (default: playtime descending)",
    )
    parser.add_argument(
        "--min-playtime", type=float, default=0,
        help="Minimum playtime in hours to include a game (default: 0 = all)",
    )
    parser.add_argument(
        "--no-steamspy", action="store_true",
        help="Skip SteamSpy API calls (faster export)",
    )
    parser.add_argument(
        "--limit", type=int, default=0,
        help="Export only top N games by playtime (0 = all)",
    )
    parser.add_argument(
        "--version", action="version",
        version=f"%(prog)s {__version__}",
    )
    args = parser.parse_args()

    if not args.key:
        parser.error("--key is required (or set STEAM_API_KEY environment variable)")
    if not args.steamid:
        parser.error("--steamid is required (or set STEAM_ID environment variable)")

    if not args.output:
        args.output = f"steam_library.{args.format}"

    cfg = {
        "key": args.key,
        "steamid": args.steamid,
        "output": args.output,
        "format": args.format,
        "sort": args.sort,
        "min_playtime": args.min_playtime,
        "limit": args.limit,
        "no_steamspy": args.no_steamspy,
    }
    run_export(cfg)


if __name__ == "__main__":
    main()
