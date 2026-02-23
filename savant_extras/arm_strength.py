"""
Arm strength leaderboard functions.

Baseball Savant provides arm strength data since 2020.
pybaseball does not support arm strength leaderboards.
"""

from __future__ import annotations

import io
import time

import pandas as pd
import requests

_BASE_URL = (
    "https://baseballsavant.mlb.com/leaderboard/arm-strength"
    "?type=player&year={year}&pos={position}"
    "&team=&minThrows={min_throws}&csv=true"
)


def arm_strength(
    year: int,
    position: str = "",
    min_throws: int = 100,
) -> pd.DataFrame:
    """
    Retrieve arm strength leaderboard data for a season.

    Parameters
    ----------
    year : int
        Season year. Data available from 2020 onward.
    position : str, default ``""``
        Filter by position. Use ``""`` for all positions,
        or one of ``"1B"``, ``"2B"``, ``"3B"``, ``"SS"``,
        ``"LF"``, ``"CF"``, ``"RF"``, ``"Outfielder"``, ``"2B/SS/3B"``.
    min_throws : int, default ``100``
        Minimum number of throws.

    Returns
    -------
    pd.DataFrame
        DataFrame with arm strength metrics including max_arm_strength,
        arm_overall, total_throws, etc.

    Raises
    ------
    requests.HTTPError
        If the Baseball Savant request fails.

    Examples
    --------
    >>> df = arm_strength(2024)
    >>> df = arm_strength(2024, position="RF", min_throws=50)
    """
    url = _BASE_URL.format(
        year=year,
        position=position,
        min_throws=min_throws,
    )

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    text = response.content.decode("utf-8")
    if not text.strip() or text.strip().startswith("<!"):
        return pd.DataFrame()

    df = pd.read_csv(io.StringIO(text))
    return df


def arm_strength_range(
    start_year: int,
    end_year: int,
    position: str = "",
    min_throws: int = 100,
) -> pd.DataFrame:
    """
    Retrieve arm strength data for multiple seasons.

    Fetches data for each year in the range and returns a combined
    DataFrame with a ``year`` column added.

    Parameters
    ----------
    start_year : int
        First season year.
    end_year : int
        Last season year (inclusive).
    position : str, default ``""``
        Filter by position.
    min_throws : int, default ``100``
        Minimum number of throws.

    Returns
    -------
    pd.DataFrame
        Combined DataFrame with a ``year`` column.

    Examples
    --------
    >>> df = arm_strength_range(2020, 2024)
    >>> df.groupby("year")["arm_overall"].mean()
    """
    frames = []

    for i, year in enumerate(range(start_year, end_year + 1)):
        if i > 0:
            time.sleep(1)
        df = arm_strength(
            year,
            position=position,
            min_throws=min_throws,
        )
        if not df.empty:
            df["year"] = year
            frames.append(df)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)
