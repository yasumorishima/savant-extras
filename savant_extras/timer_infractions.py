"""
Pitch timer infractions leaderboard functions.

Pitch clock violations (pitcher, batter, catcher, defensive shift).
Available from 2023 onward (pitch clock era).
pybaseball does not support this leaderboard.
"""

from __future__ import annotations

import io
import time

import pandas as pd
import requests

_BASE_URL = (
    "https://baseballsavant.mlb.com/leaderboard/pitch-timer-infractions"
    "?year={year}&csv=true"
)


def timer_infractions(
    year: int,
) -> pd.DataFrame:
    """
    Retrieve pitch timer infractions leaderboard for a season.

    Parameters
    ----------
    year : int
        Season year. Data available from 2023 onward (pitch clock era).

    Returns
    -------
    pd.DataFrame
        Columns include all_violations, pitcher_timer, batter_timer,
        batter_timeout, catcher_timer, defensive_shift.
    """
    url = _BASE_URL.format(year=year)
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    text = response.content.decode("utf-8")
    if not text.strip() or text.strip().startswith("<!"):
        return pd.DataFrame()

    return pd.read_csv(io.StringIO(text))


def timer_infractions_range(
    start_year: int,
    end_year: int,
) -> pd.DataFrame:
    """
    Retrieve timer infractions for multiple seasons. Adds a ``year`` column.
    """
    frames = []
    for i, year in enumerate(range(start_year, end_year + 1)):
        if i > 0:
            time.sleep(1)
        df = timer_infractions(year)
        if not df.empty:
            if "year" not in df.columns:
                df["year"] = year
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)
