"""
Bat tracking leaderboard functions with date range support.

Baseball Savant provides bat tracking data since 2024 (Hawk-Eye).
Unlike pybaseball which only supports full-season data,
savant-extras supports arbitrary date ranges for custom splits.
"""

from __future__ import annotations

import io
import time
import warnings

import pandas as pd
import requests

_HAWK_EYE_START_YEAR = 2024


_BASE_URL = (
    "https://baseballsavant.mlb.com/leaderboard/bat-tracking"
    "/swing-path-attack-angle"
    "?dateStart={start_date}&dateEnd={end_date}"
    "&gameType=Regular"
    "&minSwings={min_swings}"
    "&minGroupSwings=1"
    "&seasonStart={season_start}&seasonEnd={season_end}"
    "&type={player_type}"
    "&csv=true"
)


def bat_tracking(
    start_date: str,
    end_date: str,
    player_type: str = "batter",
    min_swings: int | str = "q",
) -> pd.DataFrame:
    """
    Retrieve bat tracking leaderboard data for a custom date range.

    This function extends pybaseball's ``statcast_batter_bat_tracking`` and
    ``statcast_pitcher_bat_tracking`` by supporting arbitrary date ranges
    instead of full-season data only.

    Bat tracking data is available from the 2024 season onward (Hawk-Eye).

    Parameters
    ----------
    start_date : str
        Start date in ``YYYY-MM-DD`` format.
    end_date : str
        End date in ``YYYY-MM-DD`` format.
    player_type : str, default ``"batter"``
        Type of player. One of ``"batter"`` or ``"pitcher"``.
    min_swings : int or str, default ``"q"``
        Minimum number of competitive swings. Use ``"q"`` for the
        qualified threshold (default on Baseball Savant).

    Returns
    -------
    pd.DataFrame
        DataFrame with bat tracking metrics including avg_bat_speed,
        swing_tilt, attack_angle, and more.

    Raises
    ------
    ValueError
        If ``player_type`` is not ``"batter"`` or ``"pitcher"``.
    requests.HTTPError
        If the Baseball Savant request fails.

    Examples
    --------
    Monthly split (April 2024):

    >>> df = bat_tracking("2024-04-01", "2024-04-30")

    First half vs second half comparison:

    >>> first_half = bat_tracking("2024-03-01", "2024-07-14")
    >>> second_half = bat_tracking("2024-07-15", "2024-11-01")

    Pitcher perspective:

    >>> df = bat_tracking("2024-04-01", "2024-06-30", player_type="pitcher")
    """
    if player_type not in ("batter", "pitcher"):
        raise ValueError(
            f"player_type must be 'batter' or 'pitcher', got {player_type!r}"
        )

    season_start = int(start_date[:4])
    season_end = int(end_date[:4])

    if season_start < _HAWK_EYE_START_YEAR:
        warnings.warn(
            f"Bat tracking data is only available from {_HAWK_EYE_START_YEAR} onward "
            f"(Hawk-Eye). Year {season_start} will likely return empty data.",
            UserWarning,
            stacklevel=2,
        )

    url = _BASE_URL.format(
        start_date=start_date,
        end_date=end_date,
        min_swings=min_swings,
        season_start=str(season_start),
        season_end=str(season_end),
        player_type=player_type,
    )

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    df = pd.read_csv(io.StringIO(response.content.decode("utf-8")))
    return df


def bat_tracking_monthly(
    year: int,
    player_type: str = "batter",
    min_swings: int | str = 1,
) -> pd.DataFrame:
    """
    Retrieve bat tracking data aggregated by month for a full season.

    Fetches data for each month of the season (April through October)
    and returns a combined DataFrame with a ``month`` column added.

    Parameters
    ----------
    year : int
        Season year. Bat tracking is available from 2024 onward.
    player_type : str, default ``"batter"``
        Type of player. One of ``"batter"`` or ``"pitcher"``.
    min_swings : int or str, default ``1``
        Minimum number of competitive swings per month.
        Defaults to 1 (lower threshold for monthly splits).

    Returns
    -------
    pd.DataFrame
        DataFrame with a ``month`` column (1-based) added, containing
        bat tracking metrics for each player-month combination.

    Examples
    --------
    >>> df = bat_tracking_monthly(2024)
    >>> df.groupby("month")["avg_bat_speed"].mean()
    """
    import calendar

    # MLB regular season: April (4) through October (10)
    season_months = range(4, 11)
    frames = []

    for i, month in enumerate(season_months):
        if i > 0:
            time.sleep(1)
        last_day = calendar.monthrange(year, month)[1]
        start = f"{year}-{month:02d}-01"
        end = f"{year}-{month:02d}-{last_day:02d}"

        df = bat_tracking(start, end, player_type=player_type, min_swings=min_swings)
        if not df.empty:
            df["month"] = month
            frames.append(df)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)


def bat_tracking_splits(
    year: int,
    player_type: str = "batter",
    min_swings: int | str = "q",
) -> dict[str, pd.DataFrame]:
    """
    Retrieve first-half and second-half bat tracking splits for a season.

    The All-Star break is approximated as July 14 (first half ends July 13).

    Parameters
    ----------
    year : int
        Season year. Bat tracking is available from 2024 onward.
    player_type : str, default ``"batter"``
        Type of player. One of ``"batter"`` or ``"pitcher"``.
    min_swings : int or str, default ``"q"``
        Minimum number of competitive swings.

    Returns
    -------
    dict[str, pd.DataFrame]
        Dictionary with keys ``"first_half"`` and ``"second_half"``.

    Examples
    --------
    >>> splits = bat_tracking_splits(2024)
    >>> first = splits["first_half"]
    >>> second = splits["second_half"]
    """
    first_half = bat_tracking(
        f"{year}-03-01",
        f"{year}-07-13",
        player_type=player_type,
        min_swings=min_swings,
    )
    second_half = bat_tracking(
        f"{year}-07-14",
        f"{year}-11-01",
        player_type=player_type,
        min_swings=min_swings,
    )
    return {"first_half": first_half, "second_half": second_half}
