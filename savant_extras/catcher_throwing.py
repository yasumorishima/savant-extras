"""
Catcher throwing leaderboard functions.

Caught stealing above average, pop time, exchange time.
pybaseball does not support this leaderboard.
"""

from __future__ import annotations

import io
import time

import pandas as pd
import requests

_BASE_URL = (
    "https://baseballsavant.mlb.com/leaderboard/catcher-throwing"
    "?year={year}&min={min_attempts}&csv=true"
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
    if not text.strip() or text.strip().startswith("<!"):
        return pd.DataFrame()

    return pd.read_csv(io.StringIO(text))


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
