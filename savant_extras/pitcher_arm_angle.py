"""
Pitcher arm angle leaderboard functions.

Release point angles and positions.
pybaseball does not support this leaderboard.
"""

from __future__ import annotations

import time

import pandas as pd
import requests

from savant_extras._http import check_season, parse_savant_csv

_BASE_URL = (
    "https://baseballsavant.mlb.com/leaderboard/pitcher-arm-angles"
    "?season={year}&team=&csv=true"
)


def pitcher_arm_angle(
    year: int,
) -> pd.DataFrame:
    """
    Retrieve pitcher arm angle leaderboard for a season.

    Parameters
    ----------
    year : int
        Season year.

    Returns
    -------
    pd.DataFrame
        Columns include ball_angle, relative_release_ball_x,
        release_ball_z, relative_shoulder_x, shoulder_z, etc.
    """
    url = _BASE_URL.format(year=year)
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    text = response.content.decode("utf-8")
    return check_season(parse_savant_csv(text, url), year, url)


def pitcher_arm_angle_range(
    start_year: int,
    end_year: int,
) -> pd.DataFrame:
    """
    Retrieve pitcher arm angle for multiple seasons. Adds a ``year`` column.
    """
    frames = []
    for i, year in enumerate(range(start_year, end_year + 1)):
        if i > 0:
            time.sleep(1)
        df = pitcher_arm_angle(year)
        if not df.empty:
            df["year"] = year
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)
