"""
Pitcher running game leaderboard functions.

Measures pitcher's ability to control the running game
(pickoffs, CS above average, etc.).
pybaseball does not support this leaderboard.
"""

from __future__ import annotations

import time

import pandas as pd
import requests

from savant_extras._http import check_season, parse_savant_csv

_BASE_URL = (
    "https://baseballsavant.mlb.com/leaderboard/pitcher-running-game"
    "?game_type=Regular&season_start={year}&season_end={year}&n={min_pa}&csv=true"
)


def running_game(
    year: int,
    min_pa: int | str = "q",
) -> pd.DataFrame:
    """
    Retrieve pitcher running game leaderboard for a season.

    Parameters
    ----------
    year : int
        Season year.
    min_pa : int or str, default ``"q"``
        Minimum running-game opportunities (Savant's ``n``; the smallest
        ``n_init`` returned equals it). ``"q"`` for qualified. The name is
        kept from earlier versions.

    Returns
    -------
    pd.DataFrame
        Columns include runs_prevented_on_running_attr, n_init, n_sb,
        n_cs, n_pk, rate_sbx, etc.
    """
    url = _BASE_URL.format(year=year, min_pa=min_pa)
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    text = response.content.decode("utf-8")
    return check_season(parse_savant_csv(text, url), year, url)


def running_game_range(
    start_year: int,
    end_year: int,
    min_pa: int | str = "q",
) -> pd.DataFrame:
    """
    Retrieve pitcher running game for multiple seasons. Adds a ``year`` column.
    """
    frames = []
    for i, year in enumerate(range(start_year, end_year + 1)):
        if i > 0:
            time.sleep(1)
        df = running_game(year, min_pa=min_pa)
        if not df.empty:
            df["year"] = year
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)
