"""
Pitch movement leaderboard functions.

Horizontal/vertical break by pitch type.
pybaseball reads the same leaderboard as
``statcast_pitcher_pitch_movement``.
"""

from __future__ import annotations

import time

import pandas as pd
import requests

from savant_extras._http import check_season, parse_savant_csv

_BASE_URL = (
    "https://baseballsavant.mlb.com/leaderboard/pitch-movement"
    "?year={year}&team=&pitch_type={pitch_type}&csv=true"
)


def pitch_movement(
    year: int,
    pitch_type: str = "FF",
) -> pd.DataFrame:
    """
    Retrieve pitch movement leaderboard for a season.

    Parameters
    ----------
    year : int
        Season year.
    pitch_type : str, default ``"FF"``
        Pitch type (e.g. ``"FF"``, ``"SL"``, ``"CU"``). Savant serves one
        pitch type per request; an empty string returns four-seamers, not
        every type. Through 0.5.0 this was sent as ``pitchType=``, which
        Savant ignores, so every call returned four-seamers whatever was
        asked for.

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
    df = check_season(parse_savant_csv(text, url), year, url)
    if pitch_type and "pitch_type" in df.columns and not df.empty:
        got = set(df["pitch_type"].dropna().unique())
        if got != {pitch_type}:
            raise ValueError(
                f"asked for pitch_type={pitch_type} but Savant returned "
                f"{sorted(got)}; the filter was ignored: {url}"
            )
    return df


def pitch_movement_range(
    start_year: int,
    end_year: int,
    pitch_type: str = "FF",
) -> pd.DataFrame:
    """
    Retrieve pitch movement for multiple seasons.

    The CSV already carries a ``year`` column, and :func:`pitch_movement`
    checks it against the season asked for; ``year`` is added only if a
    response ever lacks it.
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
