"""
Pitch tempo leaderboard functions.

Baseball Savant provides pitch tempo data since 2010.
pybaseball does not support pitch tempo leaderboards.
"""

from __future__ import annotations

import io
import time

import pandas as pd
import requests

_BASE_URL = (
    "https://baseballsavant.mlb.com/leaderboard/pitch-tempo"
    "?type={type}&season_start={year}&season_end={year}"
    "&n={min_pitches}&game_type={game_type}"
    "&split=no&with_team_only=1&csv=true"
)

_PLAYER_TYPE_MAP = {"pitcher": "Pit", "batter": "Bat"}


def pitch_tempo(
    year: int,
    player_type: str = "pitcher",
    min_pitches: int | str = "q",
    game_type: str = "Regular",
) -> pd.DataFrame:
    """
    Retrieve pitch tempo leaderboard data for a season.

    Parameters
    ----------
    year : int
        Season year. Data available from 2010 onward.
    player_type : str, default ``"pitcher"``
        Type of player. One of ``"pitcher"`` or ``"batter"``.
    min_pitches : int or str, default ``"q"``
        Minimum number of pitches. Use ``"q"`` for the qualified threshold.
    game_type : str, default ``"Regular"``
        Game type filter (e.g. ``"Regular"``).

    Returns
    -------
    pd.DataFrame
        DataFrame with pitch tempo metrics including median_seconds_empty,
        freq_hot, freq_warm, freq_cold, etc.

    Raises
    ------
    ValueError
        If ``player_type`` is not ``"pitcher"`` or ``"batter"``.
    requests.HTTPError
        If the Baseball Savant request fails.

    Examples
    --------
    >>> df = pitch_tempo(2024)
    >>> df = pitch_tempo(2024, player_type="batter")
    """
    if player_type not in _PLAYER_TYPE_MAP:
        raise ValueError(
            f"player_type must be 'pitcher' or 'batter', got {player_type!r}"
        )

    url = _BASE_URL.format(
        type=_PLAYER_TYPE_MAP[player_type],
        year=year,
        min_pitches=min_pitches,
        game_type=game_type,
    )

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    text = response.content.decode("utf-8")
    if not text.strip() or text.strip().startswith("<!"):
        return pd.DataFrame()

    df = pd.read_csv(io.StringIO(text))
    return df


def pitch_tempo_range(
    start_year: int,
    end_year: int,
    player_type: str = "pitcher",
    min_pitches: int | str = "q",
    game_type: str = "Regular",
) -> pd.DataFrame:
    """
    Retrieve pitch tempo data for multiple seasons.

    Fetches data for each year in the range and returns a combined
    DataFrame with a ``year`` column added.

    Parameters
    ----------
    start_year : int
        First season year.
    end_year : int
        Last season year (inclusive).
    player_type : str, default ``"pitcher"``
        Type of player. One of ``"pitcher"`` or ``"batter"``.
    min_pitches : int or str, default ``"q"``
        Minimum number of pitches.
    game_type : str, default ``"Regular"``
        Game type filter.

    Returns
    -------
    pd.DataFrame
        Combined DataFrame with a ``year`` column.

    Examples
    --------
    >>> df = pitch_tempo_range(2020, 2024)
    >>> df.groupby("year")["median_seconds_empty"].mean()
    """
    frames = []

    for i, year in enumerate(range(start_year, end_year + 1)):
        if i > 0:
            time.sleep(1)
        df = pitch_tempo(
            year,
            player_type=player_type,
            min_pitches=min_pitches,
            game_type=game_type,
        )
        if not df.empty:
            df["year"] = year
            frames.append(df)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)
