"""
Swing & take run value leaderboard functions.

Run values by zone (heart, shadow, chase, waste).
pybaseball reads the same leaderboard as ``statcast_batter_run_value`` /
``statcast_pitcher_run_value``.

.. note::
   Through 0.5.0 this module asked for ``type=batter``, which Savant answers
   with a header and no rows, so ``swing_take`` returned an empty frame for
   every season. The parameter is ``group`` and its values are
   case-sensitive (``Batter`` / ``Pitcher``; ``group=batter`` is empty too).
"""

from __future__ import annotations

import time

import pandas as pd
import requests

from savant_extras._http import check_season, parse_savant_csv

_BASE_URL = (
    "https://baseballsavant.mlb.com/leaderboard/swing-take"
    "?year={year}&group={group}&csv=true"
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

    url = _BASE_URL.format(year=year, group=player_type.capitalize())
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    text = response.content.decode("utf-8")
    return check_season(parse_savant_csv(text, url), year, url)


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
