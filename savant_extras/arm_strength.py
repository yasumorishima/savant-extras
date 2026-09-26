"""
Arm strength leaderboard functions.

Baseball Savant provides arm strength data since 2020.
pybaseball does not support arm strength leaderboards.
"""

from __future__ import annotations

import time

import pandas as pd
import requests

from savant_extras._http import check_season, parse_savant_csv

_BASE_URL = (
    "https://baseballsavant.mlb.com/leaderboard/arm-strength"
    "?type=player&year={year}"
    "&team=&minThrows={min_throws}&csv=true"
)


# Through 0.5.0 ``position`` was sent as ``pos=``, which Savant ignores, so
# every position returned the full table. The page's menu values are these
# column names; the filter is applied here instead.
_POSITION_COLUMNS = {
    "": None,
    "1B": "arm_1b", "2B": "arm_2b", "3B": "arm_3b", "SS": "arm_ss",
    "LF": "arm_lf", "CF": "arm_cf", "RF": "arm_rf",
    "Outfielder": "arm_of", "2B/SS/3B": "arm_inf",
}


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
    if position not in _POSITION_COLUMNS:
        raise ValueError(
            f"position must be one of {sorted(_POSITION_COLUMNS)}, got {position!r}"
        )
    column = _POSITION_COLUMNS[position]
    url = _BASE_URL.format(year=year, min_throws=min_throws)

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    text = response.content.decode("utf-8")
    df = check_season(parse_savant_csv(text, url), year, url)
    if column and not df.empty:
        # Savant's position menu only chooses which arm column the page shows;
        # the CSV always has every column. Keep the fielders measured there.
        if column not in df.columns:
            raise ValueError(f"arm strength CSV has no {column!r} column: {url}")
        df = df[df[column].notna()].reset_index(drop=True)
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
