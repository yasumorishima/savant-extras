"""
Batted ball profile leaderboard functions.

Ground ball rates, fly ball rates, pull/oppo splits, etc.
pybaseball does not support this leaderboard.
"""

from __future__ import annotations

import io
import time

import pandas as pd
import requests

_BASE_URL = (
    "https://baseballsavant.mlb.com/leaderboard/batted-ball"
    "?year={year}&type={player_type}&min={min_bbe}&csv=true"
)


def batted_ball(
    year: int,
    player_type: str = "batter",
    min_bbe: int | str = "q",
) -> pd.DataFrame:
    """
    Retrieve batted ball profile leaderboard for a season.

    Parameters
    ----------
    year : int
        Season year.
    player_type : str, default ``"batter"``
        ``"batter"`` or ``"pitcher"``.
    min_bbe : int or str, default ``"q"``
        Minimum batted ball events. ``"q"`` for qualified.

    Returns
    -------
    pd.DataFrame
        Columns include gb_rate, fb_rate, ld_rate, pull_rate, oppo_rate, etc.
    """
    if player_type not in ("batter", "pitcher"):
        raise ValueError(
            f"player_type must be 'batter' or 'pitcher', got {player_type!r}"
        )

    url = _BASE_URL.format(year=year, player_type=player_type, min_bbe=min_bbe)
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    text = response.content.decode("utf-8")
    if not text.strip() or text.strip().startswith("<!"):
        return pd.DataFrame()

    return pd.read_csv(io.StringIO(text))


def batted_ball_range(
    start_year: int,
    end_year: int,
    player_type: str = "batter",
    min_bbe: int | str = "q",
) -> pd.DataFrame:
    """
    Retrieve batted ball profile for multiple seasons. Adds a ``year`` column.
    """
    frames = []
    for i, year in enumerate(range(start_year, end_year + 1)):
        if i > 0:
            time.sleep(1)
        df = batted_ball(year, player_type=player_type, min_bbe=min_bbe)
        if not df.empty:
            df["year"] = year
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)
