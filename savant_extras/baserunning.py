"""
Baserunning run value leaderboard functions.

Total baserunning value including extra bases and stolen bases.
pybaseball does not support this leaderboard.
"""

from __future__ import annotations

import time

import pandas as pd
import requests

from savant_extras._http import check_season, parse_savant_csv

_BASE_URL = (
    "https://baseballsavant.mlb.com/leaderboard/baserunning-run-value"
    "?game_type=Regular&season_start={year}&season_end={year}&n={min_opportunities}&csv=true"
)


def baserunning(
    year: int,
    min_opportunities: int | str = "q",
) -> pd.DataFrame:
    """
    Retrieve baserunning run value leaderboard for a season.

    Parameters
    ----------
    year : int
        Season year.
    min_opportunities : int or str, default ``"q"``
        Minimum opportunities. ``"q"`` for qualified.

    Returns
    -------
    pd.DataFrame
        Columns include runner_runs_tot, runner_runs_XB, runner_runs_SBX,
        runner_runs_XB_swipe/snipe/freeze, etc.
    """
    url = _BASE_URL.format(year=year, min_opportunities=min_opportunities)
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    text = response.content.decode("utf-8")
    return check_season(parse_savant_csv(text, url), year, url)


def baserunning_range(
    start_year: int,
    end_year: int,
    min_opportunities: int | str = "q",
) -> pd.DataFrame:
    """
    Retrieve baserunning run value for multiple seasons. Adds a ``year`` column.
    """
    frames = []
    for i, year in enumerate(range(start_year, end_year + 1)):
        if i > 0:
            time.sleep(1)
        df = baserunning(year, min_opportunities=min_opportunities)
        if not df.empty:
            df["year"] = year
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)
