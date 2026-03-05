"""
Outfield Jump leaderboard from Baseball Savant.

Measures how well outfielders read and react to batted balls in the first
3 seconds after contact. Only includes plays with ≥ 90% catch probability
(Two-Star plays or harder), where judgment is most tested.

Component metrics
-----------------
outs_above_average        : int   — OAA credited from these plays
outs_per_play             : float — OAA per opportunity (rate stat)
rel_league_reaction_distance : float — feet covered in first 1.5 sec vs avg (first-step quickness)
rel_league_burst_distance    : float — feet covered in seconds 1.5–3.0 sec vs avg (acceleration)
rel_league_routing_distance  : float — routing efficiency vs avg (positive = better path)
rel_league_bootup_distance   : float — total Jump (reaction + burst + route) vs avg
f_bootup_distance            : float — raw feet covered in 3 sec (not league-adjusted)
n                            : int   — number of qualifying plays
n_outs                       : int   — actual outs recorded

pybaseball does not support this leaderboard.
"""

from __future__ import annotations

import io
import time

import pandas as pd
import requests

_BASE_URL = (
    "https://baseballsavant.mlb.com/leaderboard/outfield_jump"
    "?year={year}&type=of_jump&csv=true"
)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    ),
}


def outfield_jump(year: int) -> pd.DataFrame:
    """
    Retrieve Outfield Jump leaderboard for a season.

    Measures outfielders' ability to read and react to batted balls.
    Only includes Two-Star plays (≥90% catch probability), where elite
    routes and first steps separate great outfielders from average ones.
    pybaseball does not provide this data.

    Parameters
    ----------
    year : int
        Season year. Data available from 2016 (excluding 2020).

    Returns
    -------
    pd.DataFrame
        Jump metrics per outfielder: reaction, burst, routing efficiency,
        and overall jump vs. league average.

    Examples
    --------
    >>> from savant_extras import outfield_jump
    >>> df = outfield_jump(2024)
    >>> df.sort_values("rel_league_bootup_distance", ascending=False).head(5)
    """
    url = _BASE_URL.format(year=year)
    resp = requests.get(url, headers=_HEADERS, timeout=30)
    resp.raise_for_status()

    text = resp.content.decode("utf-8-sig")
    if not text.strip() or text.strip().startswith("<!"):
        return pd.DataFrame()

    return pd.read_csv(io.StringIO(text))


def outfield_jump_range(start_year: int, end_year: int) -> pd.DataFrame:
    """
    Retrieve Outfield Jump data for multiple seasons.

    Parameters
    ----------
    start_year : int
        First season year (2016+ excluding 2020).
    end_year : int
        Last season year (inclusive).

    Returns
    -------
    pd.DataFrame
        Combined DataFrame across all seasons.

    Examples
    --------
    >>> from savant_extras import outfield_jump_range
    >>> df = outfield_jump_range(2021, 2024)
    >>> df.groupby("year")["rel_league_bootup_distance"].mean()
    """
    frames = []
    for i, year in enumerate(range(start_year, end_year + 1)):
        if i > 0:
            time.sleep(1)
        df = outfield_jump(year)
        if not df.empty:
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)
