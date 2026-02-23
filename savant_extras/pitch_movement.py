"""
Pitch movement leaderboard functions.

Horizontal/vertical break by pitch type.
pybaseball does not support this leaderboard.
"""

from __future__ import annotations

import io
import time

import pandas as pd
import requests

_BASE_URL = (
    "https://baseballsavant.mlb.com/leaderboard/pitch-movement"
    "?year={year}&team=&pitchType={pitch_type}&csv=true"
)


def pitch_movement(
    year: int,
    pitch_type: str = "",
) -> pd.DataFrame:
    """
    Retrieve pitch movement leaderboard for a season.

    Parameters
    ----------
    year : int
        Season year.
    pitch_type : str, default ``""``
        Filter by pitch type (e.g. ``"FF"``, ``"SL"``, ``"CU"``).
        Empty string for all pitch types.

    Returns
    -------
    pd.DataFrame
        Columns include pitch_type, pitcher_break_z, pitcher_break_x,
        diff_z, diff_x, avg_speed, etc.
    """
    url = _BASE_URL.format(year=year, pitch_type=pitch_type)
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    text = response.content.decode("utf-8")
    if not text.strip() or text.strip().startswith("<!"):
        return pd.DataFrame()

    return pd.read_csv(io.StringIO(text))


def pitch_movement_range(
    start_year: int,
    end_year: int,
    pitch_type: str = "",
) -> pd.DataFrame:
    """
    Retrieve pitch movement for multiple seasons. Adds a ``year`` column.

    Note: The CSV already contains a ``year`` column from the API.
    This function adds a separate ``query_year`` column to distinguish
    the requested year from the API's year column.
    """
    frames = []
    for i, year in enumerate(range(start_year, end_year + 1)):
        if i > 0:
            time.sleep(1)
        df = pitch_movement(year, pitch_type=pitch_type)
        if not df.empty:
            if "year" not in df.columns:
                df["year"] = year
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)
