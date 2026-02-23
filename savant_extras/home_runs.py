"""
Home runs leaderboard functions.

HR distance, exit velocity, no-doubter rate, expected HR, etc.
pybaseball does not support this leaderboard.
"""

from __future__ import annotations

import io
import time

import pandas as pd
import requests

_BASE_URL = (
    "https://baseballsavant.mlb.com/leaderboard/home-runs"
    "?year={year}&type={hr_type}&min=0&csv=true"
)


def home_runs(
    year: int,
    hr_type: str = "exit_velocity",
) -> pd.DataFrame:
    """
    Retrieve home runs leaderboard for a season.

    Parameters
    ----------
    year : int
        Season year.
    hr_type : str, default ``"exit_velocity"``
        Sort/type. One of ``"exit_velocity"``, ``"adj_xhr"``, ``"distance"``.

    Returns
    -------
    pd.DataFrame
        Columns include hr_total, xhr, xhr_diff, no_doubters, avg_hr_trot, etc.
    """
    url = _BASE_URL.format(year=year, hr_type=hr_type)
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    text = response.content.decode("utf-8")
    if not text.strip() or text.strip().startswith("<!"):
        return pd.DataFrame()

    return pd.read_csv(io.StringIO(text))


def home_runs_range(
    start_year: int,
    end_year: int,
    hr_type: str = "exit_velocity",
) -> pd.DataFrame:
    """
    Retrieve home runs data for multiple seasons. Adds a ``year`` column.
    """
    frames = []
    for i, year in enumerate(range(start_year, end_year + 1)):
        if i > 0:
            time.sleep(1)
        df = home_runs(year, hr_type=hr_type)
        if not df.empty:
            df["year"] = year
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)
