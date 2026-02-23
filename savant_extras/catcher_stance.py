"""
Catcher stance leaderboard functions.

One-knee vs traditional stance metrics: framing, blocking, throwing.
pybaseball does not support this leaderboard.
"""

from __future__ import annotations

import io
import time

import pandas as pd
import requests

_BASE_URL = (
    "https://baseballsavant.mlb.com/leaderboard/catcher-stance"
    "?year={year}&min={min_pitches}&csv=true"
)


def catcher_stance(
    year: int,
    min_pitches: int | str = "q",
) -> pd.DataFrame:
    """
    Retrieve catcher stance leaderboard for a season.

    Parameters
    ----------
    year : int
        Season year.
    min_pitches : int or str, default ``"q"``
        Minimum pitches. ``"q"`` for qualified.

    Returns
    -------
    pd.DataFrame
        Columns include knee_down_pct, one_knee_framing_rv,
        one_knee_blocking_rv, one_knee_throwing_rv, catching_rv, etc.
    """
    url = _BASE_URL.format(year=year, min_pitches=min_pitches)
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    text = response.content.decode("utf-8")
    if not text.strip() or text.strip().startswith("<!"):
        return pd.DataFrame()

    return pd.read_csv(io.StringIO(text))


def catcher_stance_range(
    start_year: int,
    end_year: int,
    min_pitches: int | str = "q",
) -> pd.DataFrame:
    """
    Retrieve catcher stance for multiple seasons. Adds a ``year`` column.
    """
    frames = []
    for i, year in enumerate(range(start_year, end_year + 1)):
        if i > 0:
            time.sleep(1)
        df = catcher_stance(year, min_pitches=min_pitches)
        if not df.empty:
            df["year"] = year
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)
