"""
Home runs leaderboard functions.

HR distance, exit velocity, no-doubter rate, expected HR, etc.
pybaseball does not support this leaderboard.
"""

from __future__ import annotations

import time
import warnings

import pandas as pd
import requests

from savant_extras._http import check_season, parse_savant_csv

_BASE_URL = (
    "https://baseballsavant.mlb.com/leaderboard/home-runs"
    "?year={year}&player_type={group}&cat={category}&min={min_hr}&csv=true"
)


_CATEGORIES = ("adj_xhr", "xhr")


def home_runs(
    year: int,
    player_type: str = "batter",
    category: str = "adj_xhr",
    min_hr: int = 0,
    hr_type: str | None = None,
) -> pd.DataFrame:
    """
    Retrieve home runs leaderboard for a season.

    Parameters
    ----------
    year : int
        Season year.
    player_type : str, default ``"batter"``
        ``"batter"`` (home runs hit) or ``"pitcher"`` (home runs allowed).
    category : str, default ``"adj_xhr"``
        Expected-HR model: ``"adj_xhr"`` (park-adjusted) or ``"xhr"``.
    min_hr : int, default ``0``
        Minimum home runs.
    hr_type : str, optional
        Deprecated and ignored. Through 0.5.0 it was sent as ``type=``,
        which Savant does not read, so ``"exit_velocity"`` and
        ``"distance"`` returned the same table.

    Returns
    -------
    pd.DataFrame
        Columns include hr_total, xhr, xhr_diff, no_doubters, avg_hr_trot, etc.
    """
    if hr_type is not None:
        warnings.warn(
            "hr_type never had an effect (Savant ignores it) and is deprecated; "
            "use player_type= and category=",
            DeprecationWarning,
            stacklevel=2,
        )
    if player_type not in ("batter", "pitcher"):
        raise ValueError(
            f"player_type must be 'batter' or 'pitcher', got {player_type!r}"
        )
    if category not in _CATEGORIES:
        raise ValueError(f"category must be one of {_CATEGORIES}, got {category!r}")
    url = _BASE_URL.format(
        year=year, group=player_type.capitalize(), category=category, min_hr=int(min_hr)
    )
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    text = response.content.decode("utf-8")
    return check_season(parse_savant_csv(text, url), year, url)


def home_runs_range(
    start_year: int,
    end_year: int,
    player_type: str = "batter",
    category: str = "adj_xhr",
    min_hr: int = 0,
    hr_type: str | None = None,
) -> pd.DataFrame:
    """
    Retrieve home runs data for multiple seasons. Adds a ``year`` column.
    """
    frames = []
    for i, year in enumerate(range(start_year, end_year + 1)):
        if i > 0:
            time.sleep(1)
        df = home_runs(
            year, player_type=player_type, category=category,
            min_hr=min_hr, hr_type=hr_type,
        )
        if not df.empty:
            df["year"] = year
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)
