"""
ABS (Automated Ball-Strike) challenge leaderboard functions.

Data source: Baseball Savant ABS Challenges
(https://baseballsavant.mlb.com/leaderboard/abs-challenges)

Under the ABS challenge system the plate umpire still calls every pitch, and
a batter, pitcher or catcher may challenge the call; Hawk-Eye then decides.
Savant scores each challenger against an expected overturn rate, so the table
says not only how often a player won but how many challenges he gained or
lost compared with an average challenger facing the same pitches, and what
that was worth in runs.

pybaseball does not read this leaderboard.

Why the page and not ``csv=true``
---------------------------------
The leaderboard also answers ``csv=true``, but that export has 36 columns
and **no player id** - only a display name, which is duplicated within a
season and cannot be joined to Statcast. The page embeds the same rows
(identical counts for every level, season and challenger measured) as JSON
with 86-87 fields, including the MLBAM ``player_id`` and the run-value
columns. This module reads that JSON.

Coverage (measured 2026-09-26, regular season, ``min_challenges=1``)
--------------------------------------------------------------------
======  =====  ========  =======  =======
level   year   batter    pitcher  catcher
======  =====  ========  =======  =======
mlb     2026   526       107      107
mlb     2025   0         0        0
aaa     2026   679       202      175
aaa     2025   667       5        170
aaa     2024   0         0        0
======  =====  ========  =======  =======

MLB adopted the challenge system in 2026; Triple-A has it from 2025. 218
batters on the 2025 Triple-A board are on the 2026 MLB board (by
``player_id``; 217 by name). Counts are a snapshot and grow during a season.

Columns returned (a selection; Savant's own names)
--------------------------------------------------
challenge_type  : str   - the ``challenge_type`` asked for
player_id       : int   - MLBAM id (Savant's ``id``)
player_name, team_abbr, parent_org, level, year
n_challenges, n_overturns, n_fails (challenges the call survived),
rate_overturns, exp_chal, exp_rate_overturns, overturns_vs_exp,
n_chal_runs, exp_chal_runs, runs_vs_exp, n_strikeouts, n_walks,
n_chal_reasonable, n_chal_reasonable_opps, rate_reasonable_opp_taken,
and the ``_against`` family for challenges made against the player's side.
Catcher rows also carry ``fielder_2``.
"""

from __future__ import annotations

import json
import time
import warnings

import pandas as pd
import requests

from savant_extras._http import EmptySavantResponse

_BASE_URL = (
    "https://baseballsavant.mlb.com/leaderboard/abs-challenges"
    "?season%5B%5D={year}&level={level}"
    "&challengeType={challenge_type}&gameType%5B%5D={game_type}"
    "&minChal={min_challenges}"
)
_MARKER = "const absData = "

_LEVELS = {"mlb": "MLB", "aaa": "AAA"}
_CHALLENGE_TYPES = ("batter", "pitcher", "catcher")
_GAME_TYPES = ("R", "S")


def _extract_rows(html: str, url: str) -> list:
    at = html.find(_MARKER)
    if at < 0:
        raise ValueError(
            f"ABS challenge page no longer embeds {_MARKER.strip()!r}; "
            f"the page layout changed: {url}"
        )
    rows, _ = json.JSONDecoder().raw_decode(html[at + len(_MARKER):])
    if not isinstance(rows, list):
        raise ValueError(f"absData is {type(rows).__name__}, expected a list: {url}")
    return rows


def abs_challenges(
    year: int,
    level: str = "mlb",
    challenge_type: str = "batter",
    game_type: str = "R",
    min_challenges: int = 1,
) -> pd.DataFrame:
    """
    Retrieve the ABS challenge leaderboard for one season.

    Parameters
    ----------
    year : int
        Season. MLB has data from 2026, Triple-A from 2025.
    level : str, default ``"mlb"``
        ``"mlb"`` or ``"aaa"``.
    challenge_type : str, default ``"batter"``
        Who is challenging: ``"batter"``, ``"pitcher"`` or ``"catcher"``.
    game_type : str, default ``"R"``
        ``"R"`` (regular season) or ``"S"`` (spring training).
    min_challenges : int, default ``1``
        Minimum challenges for a player to be listed. ``0`` also lists
        players who never challenged (their ``_against`` columns can still
        be non-zero).

    Returns
    -------
    pd.DataFrame
        One row per player, keyed by ``player_id``. Empty, with an
        ``EmptySavantResponse`` warning, for a season or level with no
        challenge data.

    Raises
    ------
    ValueError
        For an unknown ``level``, ``challenge_type`` or ``game_type``; if the
        page no longer embeds the data; or if Savant answers with a different
        season or level than the one asked for (it silently ignores
        parameters it does not recognise, so this is checked, not trusted).
    """
    level_key = level.lower()
    if level_key not in _LEVELS:
        raise ValueError(f"level must be 'mlb' or 'aaa', got {level!r}")
    if challenge_type not in _CHALLENGE_TYPES:
        raise ValueError(
            f"challenge_type must be one of {_CHALLENGE_TYPES}, got {challenge_type!r}"
        )
    if game_type not in _GAME_TYPES:
        raise ValueError(f"game_type must be one of {_GAME_TYPES}, got {game_type!r}")

    url = _BASE_URL.format(
        year=int(year),
        level=level_key,
        challenge_type=challenge_type,
        game_type=game_type,
        min_challenges=int(min_challenges),
    )
    response = requests.get(url, timeout=60)
    response.raise_for_status()

    rows = _extract_rows(response.content.decode("utf-8"), url)
    if not rows:
        warnings.warn(
            f"no ABS challenge rows for {level_key} {year} ({challenge_type}): {url}",
            EmptySavantResponse,
            stacklevel=2,
        )
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    for column, expected in (("year", int(year)), ("level", _LEVELS[level_key])):
        if column not in df.columns:
            raise ValueError(f"ABS challenge data has no {column!r} field: {url}")
        got = set(df[column].astype(str).unique())
        if got != {str(expected)}:
            raise ValueError(
                f"asked for {column}={expected} but Savant returned {sorted(got)}: {url}"
            )
    if "id" not in df.columns or df["id"].isna().any():
        raise ValueError(f"ABS challenge rows without a player id: {url}")

    df = df.rename(columns={"id": "player_id"})
    df.insert(0, "challenge_type", challenge_type)
    front = ["challenge_type", "player_id", "player_name", "team_abbr",
             "parent_org", "level", "year"]
    front = [c for c in front if c in df.columns]
    return df[front + [c for c in df.columns if c not in front]]


def abs_challenges_range(
    start_year: int,
    end_year: int,
    level: str = "mlb",
    challenge_type: str = "batter",
    game_type: str = "R",
    min_challenges: int = 1,
    sleep: float = 1.0,
) -> pd.DataFrame:
    """
    Retrieve ABS challenge leaderboards for several seasons, one request per
    season (Savant keeps only the last ``season[]`` when given several).

    Seasons with no data are skipped with a warning, so
    ``abs_challenges_range(2024, 2026, level="aaa")`` returns 2025-2026.
    """
    frames = []
    for i, year in enumerate(range(start_year, end_year + 1)):
        if i > 0:
            time.sleep(sleep)
        df = abs_challenges(
            year,
            level=level,
            challenge_type=challenge_type,
            game_type=game_type,
            min_challenges=min_challenges,
        )
        if not df.empty:
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)
