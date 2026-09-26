"""
Catcher throwing leaderboard functions.

Caught stealing above average and stealing runs.
pybaseball does not read this leaderboard; it reads the separate pop-time
leaderboard (``statcast_catcher_poptime``).
"""

from __future__ import annotations

import time

import pandas as pd
import requests

from savant_extras._http import check_season, parse_savant_csv

_BASE_URL = (
    "https://baseballsavant.mlb.com/leaderboard/catcher-throwing"
    "?game_type=Regular&season_start={year}&season_end={year}&n={min_attempts}&csv=true"
)


def catcher_throwing(
    year: int,
    min_attempts: int | str = "q",
) -> pd.DataFrame:
    """
    Retrieve catcher throwing leaderboard for a season.

    Parameters
    ----------
    year : int
        Season year.
    min_attempts : int or str, default ``"q"``
        Minimum steal attempts. ``"q"`` for qualified.

    Returns
    -------
    pd.DataFrame
        Columns include catcher_stealing_runs, caught_stealing_above_average,
        pop_time, exchange_time, arm_strength, etc.
    """
    url = _BASE_URL.format(year=year, min_attempts=min_attempts)
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    text = response.content.decode("utf-8")
    return check_season(parse_savant_csv(text, url), year, url)


def catcher_throwing_range(
    start_year: int,
    end_year: int,
    min_attempts: int | str = "q",
) -> pd.DataFrame:
    """
    Retrieve catcher throwing for multiple seasons. Adds a ``year`` column.
    """
    frames = []
    for i, year in enumerate(range(start_year, end_year + 1)):
        if i > 0:
            time.sleep(1)
        df = catcher_throwing(year, min_attempts=min_attempts)
        if not df.empty:
            df["year"] = year
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)
