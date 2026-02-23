"""
Swing & take run value leaderboard functions.

Run values by zone (heart, shadow, chase, waste).
pybaseball does not support this leaderboard.
"""

from __future__ import annotations

import io
import time

import pandas as pd
import requests

_BASE_URL = (
    "https://baseballsavant.mlb.com/leaderboard/swing-take"
    "?year={year}&type={player_type}&csv=true"
)


def swing_take(
    year: int,
    player_type: str = "batter",
) -> pd.DataFrame:
    """
    Retrieve swing & take run value leaderboard for a season.

    Parameters
    ----------
    year : int
        Season year.
    player_type : str, default ``"batter"``
        ``"batter"`` or ``"pitcher"``.

    Returns
    -------
    pd.DataFrame
        Columns include runs_all, runs_heart, runs_shadow,
        runs_chase, runs_waste, etc.
    """
    if player_type not in ("batter", "pitcher"):
        raise ValueError(
            f"player_type must be 'batter' or 'pitcher', got {player_type!r}"
        )

    url = _BASE_URL.format(year=year, player_type=player_type)
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    text = response.content.decode("utf-8")
    if not text.strip() or text.strip().startswith("<!"):
        return pd.DataFrame()

    return pd.read_csv(io.StringIO(text))


def swing_take_range(
    start_year: int,
    end_year: int,
    player_type: str = "batter",
) -> pd.DataFrame:
    """
    Retrieve swing & take data for multiple seasons. Adds a ``year`` column.
    """
    frames = []
    for i, year in enumerate(range(start_year, end_year + 1)):
        if i > 0:
            time.sleep(1)
        df = swing_take(year, player_type=player_type)
        if not df.empty:
            df["year"] = year
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)
