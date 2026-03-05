"""
Outs Above Average (OAA) defensive leaderboard from Baseball Savant.

Measures how many outs a fielder saves (or costs) relative to an average
fielder at the same position. Includes directional breakdowns and
catch-probability-adjusted success rates.

pybaseball does not support this leaderboard.

Columns returned (key)
-----------------------
last_name, first_name : str   — player name
player_id             : int   — MLB player ID
display_team_name     : str   — team name
year                  : int   — season year
primary_pos_formatted : str   — primary defensive position
outs_above_average    : int   — total OAA
outs_above_average_infront    : int — OAA on balls in front
outs_above_average_lateral_toward3bline : int — OAA toward 3B
outs_above_average_lateral_toward1bline : int — OAA toward 1B
outs_above_average_behind     : int — OAA on balls behind
outs_above_average_rhh        : int — OAA vs RHH
outs_above_average_lhh        : int — OAA vs LHH
fielding_runs_prevented       : int — run value of defense
actual_success_rate_formatted : str — actual catch % (e.g. "88%")
adj_estimated_success_rate_formatted : str — expected catch % (e.g. "86%")
diff_success_rate_formatted   : str — catch % above/below expected
"""

from __future__ import annotations

import io
import time

import pandas as pd
import requests

_BASE_URL = (
    "https://baseballsavant.mlb.com/leaderboard/outs_above_average"
    "?type=Fielder&startYear={year}&endYear={year}"
    "&split=no&team=&range=year&min={min_opp}&pos=&roles=&viz=show&csv=true"
)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    ),
}


def outs_above_average(
    year: int,
    min_opp: int | str = "q",
    pos: str = "",
) -> pd.DataFrame:
    """
    Retrieve Outs Above Average (OAA) defensive leaderboard for a season.

    OAA measures how many outs a fielder saves (positive) or costs (negative)
    relative to an average fielder. Based on catch probability of each batted ball.
    pybaseball does not provide this data.

    Parameters
    ----------
    year : int
        Season year (e.g. 2024).
    min_opp : int or str, default ``"q"``
        Minimum fielding opportunities. Use ``"q"`` for MLB-qualified minimum,
        or an integer (e.g. 50).
    pos : str, default ``""``
        Position filter. Use ``""`` for all positions,
        or one of ``"1B"``, ``"2B"``, ``"3B"``, ``"SS"``, ``"LF"``, ``"CF"``, ``"RF"``.

    Returns
    -------
    pd.DataFrame
        OAA metrics including directional breakdowns, catch probabilities,
        and fielding runs prevented.

    Examples
    --------
    >>> from savant_extras import outs_above_average
    >>> df = outs_above_average(2024)
    >>> df.sort_values("outs_above_average", ascending=False).head(5)
    """
    url = _BASE_URL.format(year=year, min_opp=min_opp)
    if pos:
        url += f"&pos={pos}"

    resp = requests.get(url, headers=_HEADERS, timeout=30)
    resp.raise_for_status()

    text = resp.content.decode("utf-8-sig")
    if not text.strip() or text.strip().startswith("<!"):
        return pd.DataFrame()

    return pd.read_csv(io.StringIO(text))


def outs_above_average_range(
    start_year: int,
    end_year: int,
    min_opp: int | str = "q",
    pos: str = "",
) -> pd.DataFrame:
    """
    Retrieve OAA data for multiple seasons.

    Parameters
    ----------
    start_year : int
        First season year.
    end_year : int
        Last season year (inclusive).
    min_opp : int or str, default ``"q"``
        Minimum fielding opportunities.
    pos : str, default ``""``
        Position filter.

    Returns
    -------
    pd.DataFrame
        Combined DataFrame across all seasons.

    Examples
    --------
    >>> from savant_extras import outs_above_average_range
    >>> df = outs_above_average_range(2022, 2024)
    >>> df.groupby("year")["outs_above_average"].sum()
    """
    frames = []
    for i, year in enumerate(range(start_year, end_year + 1)):
        if i > 0:
            time.sleep(1)
        df = outs_above_average(year, min_opp=min_opp, pos=pos)
        if not df.empty:
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)
