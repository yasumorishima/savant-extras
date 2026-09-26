"""
Year-to-year changes leaderboard functions.

Compare a player's stat (xwOBA by default) across seasons.
pybaseball does not support this leaderboard.
"""

from __future__ import annotations


import pandas as pd
import requests

from savant_extras._http import parse_savant_csv

_BASE_URL = (
    "https://baseballsavant.mlb.com/leaderboard/statcast-year-to-year"
    "?year={year}&group={group}&type={stat}&csv=true"
)


_STATS = ("ba", "xba", "obp", "xobp", "slg", "xslg", "iso", "xiso",
          "babip", "woba", "xwoba", "wobacon")


def year_to_year(
    year: int,
    player_type: str = "batter",
    stat: str = "xwoba",
) -> pd.DataFrame:
    """
    Retrieve year-to-year xwOBA changes leaderboard.

    Parameters
    ----------
    year : int
        Season year (the latest year shown).
    player_type : str, default ``"batter"``
        ``"batter"`` or ``"pitcher"``.
    stat : str, default ``"xwoba"``
        The statistic compared across seasons: one of ``ba``, ``xba``,
        ``obp``, ``xobp``, ``slg``, ``xslg``, ``iso``, ``xiso``, ``babip``,
        ``woba``, ``xwoba``, ``wobacon``. Through 0.5.0 this module sent the
        player side as ``type=``, which is where Savant reads the statistic,
        so every call returned batters and a statistic that was not xwOBA.

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

    if stat not in _STATS:
        raise ValueError(f"stat must be one of {_STATS}, got {stat!r}")
    url = _BASE_URL.format(year=year, group=player_type.capitalize(), stat=stat)
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    text = response.content.decode("utf-8")
    return parse_savant_csv(text, url)
