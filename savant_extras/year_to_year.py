"""
Year-to-year changes leaderboard functions.

Compare a player's expected stats (xwOBA) across seasons.
pybaseball does not support this leaderboard.
"""

from __future__ import annotations

import io

import pandas as pd
import requests

_BASE_URL = (
    "https://baseballsavant.mlb.com/leaderboard/statcast-year-to-year"
    "?year={year}&type={player_type}&csv=true"
)


def year_to_year(
    year: int,
    player_type: str = "batter",
) -> pd.DataFrame:
    """
    Retrieve year-to-year xwOBA changes leaderboard.

    Parameters
    ----------
    year : int
        Season year (the latest year shown).
    player_type : str, default ``"batter"``
        ``"batter"`` or ``"pitcher"``.

    Returns
    -------
    pd.DataFrame
        Columns include name, entity_id, and xwOBA values for each
        season plus delta columns between consecutive years.
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
