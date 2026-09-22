"""
MLB Park Factors from FanGraphs Guts! - the pre-0.5.0 source, kept.

Data source: https://www.fangraphs.com/guts.aspx?type=pf

``park_factors`` moved to Baseball Savant in 0.5.0 because this package is a
Savant package and Savant publishes park factors. This module keeps the
FanGraphs table available, because it is the only one of the two that has
``pf_5yr`` and ``pf_fip``, and because the two scales disagree - COL 2024 is
``pf_hr`` 131 here and 109 on the Savant index.

Access
------
FanGraphs sits behind Cloudflare, and what it challenges is the User-Agent,
not the client. Measured 2026-09-23 from a residential line:

  ``Mozilla/5.0 ... Chrome/140``      -> 403, ``cf-mitigated: challenge``
  ``Mozilla/5.0 ... Chrome/120``      -> 403, ``cf-mitigated: challenge``
  no UA / ``curl/8.5.0`` / this one   -> 200, 151,750 bytes of real page

So this module says who it is instead of impersonating a browser. Up to
0.4.4 it sent a Chrome UA and was challenged every time, which is why it
returned an empty frame for every season.

That fixes the User-Agent half only. Datacenter addresses are blocked
separately: on GitHub Actions run 35565978836 (2026-09-21), pybaseball -
which sets no User-Agent at all, so it sends the honest default - still got
403 for all 12 seasons. Expect this module to work from a home connection
and not from a cloud runner.

Columns returned
----------------
season, team, pf_5yr, pf_3yr, pf_1yr, pf_hr, pf_1b, pf_2b, pf_3b, pf_so,
pf_bb, pf_fip. 100 = neutral, >100 = hitter-friendly.
"""

from __future__ import annotations

import time
import warnings
from io import StringIO

import pandas as pd
import requests

from savant_extras.park_factors import _NAME_TO_ABB

_BASE_URL = "https://www.fangraphs.com/guts.aspx?type=pf&teamid=0&season={year}"

_HEADERS = {
    "User-Agent": "savant-extras (+https://github.com/yasumorishima/savant-extras)",
    "Referer": "https://www.fangraphs.com/",
}

# FanGraphs HTML header -> clean name
_COL_RENAME: dict[str, str] = {
    "Basic (5yr)":  "pf_5yr",
    "Basic":        "pf_5yr",   # older page variant
    "3yr":          "pf_3yr",
    "1yr":          "pf_1yr",
    "HR":           "pf_hr",
    "1B":           "pf_1b",
    "2B":           "pf_2b",
    "3B":           "pf_3b",
    "SO":           "pf_so",
    "BB":           "pf_bb",
    "FIP":          "pf_fip",
    "uBB":          "pf_bb",    # unintentional BB, alias
    "Runs":         "pf_runs",
}

_PF_COLS = ["pf_5yr", "pf_3yr", "pf_1yr", "pf_hr", "pf_1b",
            "pf_2b", "pf_3b", "pf_so", "pf_bb", "pf_fip"]


def _abbrev(name: str) -> str | None:
    for key, abb in _NAME_TO_ABB.items():
        if key in str(name):
            return abb
    return None


def _fetch_one(year: int) -> pd.DataFrame:
    resp = requests.get(_BASE_URL.format(year=year), headers=_HEADERS, timeout=30)
    resp.raise_for_status()

    # StringIO wrap required for pandas 2.0+ (a raw string triggers lxml
    # file-path detection).
    tables = pd.read_html(StringIO(resp.text))
    target = None
    for t in tables:
        if any("Team" in str(c) for c in t.columns):
            target = t
            break
    if target is None:
        raise ValueError(
            f"Park factor table not found for {year}. "
            f"The page may have changed structure, or Cloudflare served a "
            f"challenge page instead of the table."
        )

    target.columns = [
        str(c[-1]).strip() if isinstance(c, tuple) else str(c).strip()
        for c in target.columns
    ]
    team_col = next((c for c in target.columns if c == "Team"), None)
    if team_col is None:
        raise ValueError(f"'Team' column not found for {year}. "
                         f"Columns: {target.columns.tolist()}")

    target = target.rename(columns=_COL_RENAME)
    target["team"] = target[team_col].apply(_abbrev)
    target["season"] = year
    target = target.dropna(subset=["team"])

    keep = ["season", "team"] + [c for c in _PF_COLS if c in target.columns]
    target = target[keep].copy()
    for col in target.columns:
        if col not in ("season", "team"):
            target[col] = pd.to_numeric(target[col], errors="coerce")
    return target.reset_index(drop=True)


def park_factors_fangraphs(season: int) -> pd.DataFrame:
    """
    FanGraphs park factors for one season.

    Parameters
    ----------
    season : int
        MLB season year.

    Returns
    -------
    pd.DataFrame
        One row per club. See the module docstring for the columns.

    Raises
    ------
    ValueError
        If the page carries no park factor table - which is also what a
        Cloudflare challenge page looks like.
    requests.HTTPError
        If FanGraphs refuses the request.
    """
    return _fetch_one(season)


def park_factors_fangraphs_range(start_season: int, end_season: int,
                                 sleep: float = 1.5) -> pd.DataFrame:
    """
    FanGraphs park factors for several seasons, concatenated.

    Returns an empty DataFrame with a warning when every season fails, which
    is what a blocked network looks like.
    """
    frames: list[pd.DataFrame] = []
    failures: list[str] = []
    for year in range(start_season, end_season + 1):
        try:
            frames.append(_fetch_one(year))
            print(f"  park_factors_fangraphs {year}: fetched")
        except Exception as exc:
            failures.append(f"{year} ({exc})")
            print(f"  park_factors_fangraphs {year}: FAILED - {exc}")
        if year < end_season:
            time.sleep(sleep)

    if not frames:
        warnings.warn(
            "park_factors_fangraphs_range: no data fetched for any season. "
            "FanGraphs blocks datacenter addresses - measured on a GitHub "
            "runner 2026-09-21. Returning empty DataFrame.",
            UserWarning,
            stacklevel=2,
        )
        return pd.DataFrame()
    if failures:
        warnings.warn(
            "park_factors_fangraphs_range: skipped " + "; ".join(failures),
            UserWarning,
            stacklevel=2,
        )
    return pd.concat(frames, ignore_index=True)
