"""
Stuff+ / Location+ / Pitching+ leaderboard from FanGraphs.

These pitcher quality metrics are NOT available in pybaseball.

- **Stuff+** (sp_stuff): How good the physical pitch characteristics are
  (velocity, movement, spin), on a scale where 100 = MLB average.
- **Location+** (sp_location): How well pitches are located within counts
  and pitch types, independent of stuff.
- **Pitching+** (sp_pitching): Combined quality of stuff + location.

Per-pitch-type variants are also available (sp_s_FA, sp_l_FA, etc. for
Fastball Stuff+, Fastball Location+, etc.).

Data source: FanGraphs Leaders (type=36), extracted from SSR JSON.
Data available from 2020 onward (model trained on 2020+ Statcast data).

Columns returned (key)
-----------------------
name         : str   — player name
team         : str   — team abbreviation
season       : int   — MLB season year
age          : int   — player age
ip           : float — innings pitched
mlbam_id     : int   — MLB MLBAM player ID (for joining with Statcast)
stuff_plus   : float — overall Stuff+ (100 = avg)
location_plus: float — overall Location+ (100 = avg)
pitching_plus: float — overall Pitching+ (100 = avg)
stuff_fa     : float — Stuff+ for Four-Seam Fastball (if thrown)
stuff_si     : float — Stuff+ for Sinker
stuff_fc     : float — Stuff+ for Cutter
stuff_sl     : float — Stuff+ for Slider
stuff_cu     : float — Stuff+ for Curveball
stuff_ch     : float — Stuff+ for Changeup
loc_fa       : float — Location+ for Four-Seam Fastball
loc_si       : float — Location+ for Sinker
... (same pattern for fc, sl, cu, ch)
"""

from __future__ import annotations

import json
import re
import time

import pandas as pd
import requests

_BASE_URL = (
    "https://www.fangraphs.com/leaders.aspx"
    "?pos=all&stats=pit&lg=al%2Cnl&qual=0&type=36"
    "&season={year}&season1={year}&ind=0&team=0&rost=0"
    "&age=0&filter=&players=0&startdate=&enddate="
)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    ),
    "Referer": "https://www.fangraphs.com/",
}

# FanGraphs field → clean column name
_COL_MAP = {
    "Name":       "name",
    "Team":       "team",
    "Season":     "season",
    "Age":        "age",
    "IP":         "ip",
    "xMLBAMID":   "mlbam_id",
    "sp_stuff":   "stuff_plus",
    "sp_location":"location_plus",
    "sp_pitching":"pitching_plus",
    # per-pitch Stuff+
    "sp_s_FA": "stuff_fa", "sp_s_SI": "stuff_si", "sp_s_FC": "stuff_fc",
    "sp_s_SL": "stuff_sl", "sp_s_CU": "stuff_cu", "sp_s_CH": "stuff_ch",
    "sp_s_ST": "stuff_st", "sp_s_FS": "stuff_fs",
    # per-pitch Location+
    "sp_l_FA": "loc_fa",   "sp_l_SI": "loc_si",   "sp_l_FC": "loc_fc",
    "sp_l_SL": "loc_sl",   "sp_l_CU": "loc_cu",   "sp_l_CH": "loc_ch",
    "sp_l_ST": "loc_st",   "sp_l_FS": "loc_fs",
    # per-pitch Pitching+
    "sp_p_FA": "pit_fa",   "sp_p_SI": "pit_si",   "sp_p_FC": "pit_fc",
    "sp_p_SL": "pit_sl",   "sp_p_CU": "pit_cu",   "sp_p_CH": "pit_ch",
    "sp_p_ST": "pit_st",   "sp_p_FS": "pit_fs",
}


def _fetch_one(year: int) -> pd.DataFrame:
    url = _BASE_URL.format(year=year)
    resp = requests.get(url, headers=_HEADERS, timeout=30)
    resp.raise_for_status()

    # Extract __NEXT_DATA__ SSR JSON embedded in the page
    match = re.search(
        r'<script id="__NEXT_DATA__"[^>]*>([^<]+)</script>',
        resp.text,
    )
    if not match:
        raise ValueError(
            f"__NEXT_DATA__ JSON not found for {year}. "
            "FanGraphs page structure may have changed."
        )

    raw = json.loads(match.group(1))

    # Navigate to player data array
    try:
        queries = raw["props"]["pageProps"]["dehydratedState"]["queries"]
        players = queries[0]["state"]["data"]["data"]
    except (KeyError, IndexError) as exc:
        raise ValueError(
            f"Unexpected JSON structure for {year}: {exc}"
        ) from exc

    if not players:
        return pd.DataFrame()

    df = pd.DataFrame(players)

    # Rename known columns, keep only mapped ones
    existing_map = {k: v for k, v in _COL_MAP.items() if k in df.columns}
    df = df.rename(columns=existing_map)
    keep = [v for k, v in _COL_MAP.items() if k in df.columns]
    df = df[keep].copy()

    # Ensure season column
    if "season" not in df.columns:
        df["season"] = year

    # Numeric conversion
    for col in df.columns:
        if col not in ("name", "team"):
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df.reset_index(drop=True)


def pitcher_quality(year: int) -> pd.DataFrame:
    """
    Retrieve Stuff+ / Location+ / Pitching+ leaderboard for a season.

    These FanGraphs pitcher quality metrics are NOT available in pybaseball.
    Data is extracted from FanGraphs' server-side rendered JSON (type=36).
    Available from 2020 onward.

    Parameters
    ----------
    year : int
        Season year (2020+).

    Returns
    -------
    pd.DataFrame
        Pitcher quality metrics including overall Stuff+/Location+/Pitching+
        and per-pitch-type breakdowns (FA/SI/FC/SL/CU/CH/ST/FS).

    Examples
    --------
    >>> from savant_extras import pitcher_quality
    >>> df = pitcher_quality(2024)
    >>> df.sort_values("stuff_plus", ascending=False).head(10)
    """
    return _fetch_one(year)


def pitcher_quality_range(
    start_year: int,
    end_year: int,
    sleep: float = 2.0,
) -> pd.DataFrame:
    """
    Retrieve Stuff+ / Location+ / Pitching+ for multiple seasons.

    Parameters
    ----------
    start_year : int
        First season year (2020+).
    end_year : int
        Last season year (inclusive).
    sleep : float, default 2.0
        Seconds to wait between requests.

    Returns
    -------
    pd.DataFrame
        Combined DataFrame across all seasons.

    Examples
    --------
    >>> from savant_extras import pitcher_quality_range
    >>> df = pitcher_quality_range(2022, 2024)
    >>> df.groupby("season")["stuff_plus"].mean()
    """
    frames = []
    for i, year in enumerate(range(start_year, end_year + 1)):
        if i > 0:
            time.sleep(sleep)
        try:
            df = _fetch_one(year)
            frames.append(df)
            print(f"  pitcher_quality {year}: {len(df)} pitchers fetched")
        except Exception as exc:
            print(f"  pitcher_quality {year}: FAILED — {exc}")

    if not frames:
        raise RuntimeError(
            "No pitcher quality data fetched. "
            "Check network connectivity or FanGraphs page structure."
        )
    return pd.concat(frames, ignore_index=True)
