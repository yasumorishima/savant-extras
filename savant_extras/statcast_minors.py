"""
Pitch-level Statcast for the minor leagues.

Data source: Baseball Savant Statcast Search with ``minors=true``
(https://baseballsavant.mlb.com/statcast-search-minors)

Hawk-Eye has run in every Triple-A park since 2023, and Savant serves those
pitches through the same search as the majors, with the same columns
(119 on 2025-06-10).
pybaseball's ``statcast()`` has no minors switch, so this is the way to get
them as a DataFrame.

What is filled, Triple-A (one day sampled per season, measured 2026-09-26)
-------------------------------------------------------------------------
* ``release_speed``, ``release_spin_rate``, ``pfx_x``/``pfx_z``,
  ``launch_speed``/``launch_angle`` and the rest of the ball-flight columns.
* ``arm_angle``: 93-99% of pitches from 2023 on (16% in 2022).
* **Bat tracking is not**: ``bat_speed``, ``swing_length``,
  ``attack_angle``, ``swing_path_tilt`` and the ``intercept_*`` columns are
  empty in every Triple-A season.

2022 is partial (about a third of pitches carry spin), 2021 returns nothing.
``level="A"`` returned only Florida State League clubs on the day sampled;
Double-A returned no rows.

.. warning::
   Leave out ``minors=true`` and Savant ignores ``hfLevel`` - you get zero
   rows from this search form, and MLB pitches from some others. This
   function always sends both, and :func:`statcast_minors` checks that no
   game it returns is a major-league game.
"""

from __future__ import annotations

import datetime as dt
import time
import warnings

import pandas as pd
import requests

from savant_extras._http import EmptySavantResponse, parse_savant_csv

_BASE_URL = (
    "https://baseballsavant.mlb.com/statcast_search/csv"
    "?all=true&type=details&minors=true"
    "&hfGT={game_type}%7C&hfSea={season}%7C&hfLevel={level}%7C"
    "&player_type={player_type}"
    "&game_date_gt={day}&game_date_lt={day}"
)

_LEVELS = ("AAA", "A")
_ROW_CAP = 25000  # Savant truncates a single search at this many rows
_RETRIES = 3


def _get(url: str) -> requests.Response:
    """GET with a short retry on 5xx and connection errors (a season is
    ~180 requests; one transient failure should not discard the rest)."""
    for attempt in range(_RETRIES):
        try:
            response = requests.get(url, timeout=60)
        except (requests.ConnectionError, requests.Timeout):
            if attempt == _RETRIES - 1:
                raise
        else:
            if response.status_code < 500 or attempt == _RETRIES - 1:
                response.raise_for_status()
                return response
        time.sleep(2 ** (attempt + 1))
    raise AssertionError("unreachable")


def _days(start_date: str, end_date: str):
    start = dt.date.fromisoformat(start_date)
    end = dt.date.fromisoformat(end_date)
    if end < start:
        raise ValueError(f"end_date {end_date} is before start_date {start_date}")
    day = start
    while day <= end:
        yield day
        day += dt.timedelta(days=1)


def statcast_minors(
    start_date: str,
    end_date: str,
    level: str = "AAA",
    player_type: str = "pitcher",
    game_type: str = "R",
    sleep: float = 1.0,
) -> pd.DataFrame:
    """
    Retrieve pitch-by-pitch minor-league Statcast for a date range.

    One request is made per day (a day of Triple-A is about 4,500 pitches,
    well under Savant's 25,000-row cap), so a full season is roughly 180
    requests and takes a few minutes at the default ``sleep``.

    Parameters
    ----------
    start_date, end_date : str
        Inclusive, ``YYYY-MM-DD``. Must fall in one season.
    level : str, default ``"AAA"``
        ``"AAA"`` or ``"A"``.
    player_type : str, default ``"pitcher"``
        ``"pitcher"`` or ``"batter"``; decides which player the
        ``player_name`` column names. The pitches are the same.
    game_type : str, default ``"R"``
        Savant game type code (``"R"`` regular season).
    sleep : float, default ``1.0``
        Seconds between daily requests.

    Returns
    -------
    pd.DataFrame
        Savant's Statcast search columns, one row per pitch. Days with no
        games (off days, before the season) contribute nothing and do not
        warn; a range with no pitches at all returns an empty frame and
        warns once.

    Raises
    ------
    ValueError
        For an unknown ``level``/``player_type``, a range that crosses
        seasons, or a response containing major-league games.
    """
    if level not in _LEVELS:
        raise ValueError(f"level must be one of {_LEVELS}, got {level!r}")
    if player_type not in ("pitcher", "batter"):
        raise ValueError(
            f"player_type must be 'pitcher' or 'batter', got {player_type!r}"
        )
    days = list(_days(start_date, end_date))
    seasons = {d.year for d in days}
    if len(seasons) != 1:
        raise ValueError(f"date range spans seasons {sorted(seasons)}; split it")
    season = seasons.pop()

    frames = []
    for i, day in enumerate(days):
        if i > 0:
            time.sleep(sleep)
        url = _BASE_URL.format(
            game_type=game_type,
            season=season,
            level=level,
            player_type=player_type,
            day=day.isoformat(),
        )
        text = _get(url).content.decode("utf-8")
        body = text.strip()
        if not body or body.startswith("<"):
            # an error page, not an off day: say so and carry on
            kind = "an HTML page" if body else "an empty body"
            warnings.warn(
                f"{day}: Baseball Savant returned "
                f"{kind} instead of CSV "
                f"- that day is missing: {url}",
                EmptySavantResponse,
                stacklevel=2,
            )
            continue
        with warnings.catch_warnings():
            # a header with no rows is an off day, judged once below
            warnings.simplefilter("ignore", EmptySavantResponse)
            df = parse_savant_csv(text, url)
        if df.empty:
            continue
        if len(df) >= _ROW_CAP:
            warnings.warn(
                f"{day}: {len(df)} rows hit Savant's {_ROW_CAP}-row cap; "
                "pitches on that day are missing",
                stacklevel=2,
            )
        frames.append(df)

    if not frames:
        warnings.warn(
            f"no {level} pitches between {start_date} and {end_date}",
            EmptySavantResponse,
            stacklevel=2,
        )
        return pd.DataFrame()

    out = pd.concat(frames, ignore_index=True)
    if {"home_team", "away_team", "game_pk"} <= set(out.columns):
        mlb = _major_league_games(out)
        if mlb:
            raise ValueError(
                f"Savant returned major-league games {sorted(mlb)[:5]} for a "
                f"{level} request; the minors filter was ignored"
            )
    return out


# Major-league club abbreviations as Savant writes them. A minor-league
# response containing a game between two of these is a major-league game.
# Both teams are required because one abbreviation is shared: ``COL`` is
# Colorado in MLB and Columbus in Triple-A (the only overlap among the 30
# Triple-A clubs seen on 2025-06-10).
_MLB_TEAMS = frozenset(
    "ATH AZ ATL BAL BOS CHC CIN CLE COL CWS DET HOU KC LAA LAD MIA MIL MIN "
    "NYM NYY OAK PHI PIT SD SEA SF STL TB TEX TOR WSH".split()
)


def _major_league_games(df: pd.DataFrame) -> set:
    both = df["home_team"].isin(_MLB_TEAMS) & df["away_team"].isin(_MLB_TEAMS)
    return set(df.loc[both, "game_pk"].unique())
