"""
Shared parsing for Baseball Savant CSV responses.

Savant answers a bad request with HTTP 200 and either an HTML page or a CSV
that has a header and no rows. Through 0.5.0 every function turned both into
an empty DataFrame without a word, which is how ``swing_take`` returned
nothing for every season while looking healthy (the parameter was wrong).
An empty result can be legitimate - a season with no data yet, a filter
nobody qualifies for - so this warns rather than raises.
"""

from __future__ import annotations

import io
import warnings

import pandas as pd


class EmptySavantResponse(UserWarning):
    """Savant returned HTML or a header-only CSV for a leaderboard request."""


def parse_savant_csv(text: str, url: str) -> pd.DataFrame:
    """
    Parse a Savant CSV body, warning when it holds no rows.

    Parameters
    ----------
    text : str
        Decoded response body.
    url : str
        The request URL, quoted in the warning so the caller can open it.

    Returns
    -------
    pd.DataFrame
        The parsed table. Empty (no columns) for an empty or HTML body;
        header-only CSVs keep their columns and have zero rows.
    """
    body = text.strip()
    if not body or body.startswith("<"):
        kind = "an HTML page" if body else "an empty body"
        warnings.warn(
            f"Baseball Savant returned {kind} instead of CSV for {url}",
            EmptySavantResponse,
            stacklevel=3,
        )
        return pd.DataFrame()

    df = pd.read_csv(io.StringIO(text))
    if df.empty:
        warnings.warn(
            "Baseball Savant returned a CSV header with no rows for "
            f"{url} - check the parameters, or the season may have no data",
            EmptySavantResponse,
            stacklevel=3,
        )
    return df


def check_season(df: pd.DataFrame, year: int, url: str) -> pd.DataFrame:
    """
    Raise if the rows Savant sent belong to a different season.

    Savant serves the current season when it does not recognise the season
    parameter, with HTTP 200 and a full table. Through 0.5.0 eight functions
    here sent a parameter Savant had stopped reading, so every "2024" or
    "2025" call returned the 2026 table under the requested year. Checked
    whenever the table carries a season column.
    """
    for column in ("year", "start_year", "season"):
        if column in df.columns and not df.empty:
            got = set(pd.to_numeric(df[column], errors="coerce").dropna().astype(int))
            if got and got != {int(year)}:
                raise ValueError(
                    f"asked for season {year} but Savant returned {sorted(got)} "
                    f"in column {column!r}; the season parameter was ignored: {url}"
                )
            break
    return df
