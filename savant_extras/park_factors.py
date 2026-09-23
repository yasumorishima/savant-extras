"""
MLB Park Factors from Baseball Savant.

Data source: Baseball Savant Statcast Park Factors
(https://baseballsavant.mlb.com/leaderboard/statcast-park-factors)

.. note::
   **Source changed in 0.5.0.** Through 0.4.4 ``park_factors`` scraped
   FanGraphs Guts! (``fangraphs.com/guts.aspx?type=pf``) - in a package
   whose every other function reads Baseball Savant. It now reads Savant
   too. The FanGraphs scraper is still here as
   :func:`park_factors_fangraphs`, and it works; see that function for what
   only it can give you (``pf_5yr``, ``pf_fip``).

   **Columns kept their names but changed their meaning.** ``pf_hr``,
   ``pf_1b``, ``pf_2b``, ``pf_3b``, ``pf_so``, ``pf_bb`` and the runs factor
   now come from Savant's index rather than FanGraphs', and the two do not
   agree: COL 2024 is ``pf_hr`` 109 here and 131 on the FanGraphs scale.
   Pin ``savant-extras<0.5`` if you need the old numbers, or call
   :func:`park_factors_fangraphs`.

Columns returned
----------------
season        : int    - MLB season year (the year asked for)
team          : str    - team abbreviation (COL, BOS, ...)
venue_id      : int    - MLB venue id
venue_name    : str    - ballpark name as Savant spells it
n_pa_1yr      : int    - plate appearances behind the single-season index
n_pa_3yr      : float  - plate appearances behind the 3-year index
pf_1yr        : float  - runs park factor, ``season`` alone
pf_3yr        : float  - runs park factor, 3-year window ending at ``season``
pf_3yr_years  : str    - the window Savant used for the 3-year columns
pf_hr / pf_1b / pf_2b / pf_3b / pf_so / pf_bb / pf_obp / pf_hits /
pf_woba / pf_wobacon / pf_xwobacon / pf_bacon / pf_xbacon /
pf_hardhit / pf_wobatto : float

All factors: 100 = neutral, >100 = hitter-friendly, <100 = pitcher-friendly.
For a pitching park factor the values invert (Coors is bad for pitchers).

``season``, ``team``, ``venue_id``, ``venue_name``, ``pf_1yr`` and
``n_pa_1yr`` describe the single season. Every other column comes from the
3-year window, matching how FanGraphs regressed its single-season columns;
``pf_3yr_years`` records which window that was.

Every factor column is float64 in every season. Savant sends the indices as
strings, and letting pandas infer would make a column int64 in the seasons
with no gaps and float64 in the seasons with one - so ``astype(int)`` would
work on 2024 and raise on 2020.

Coverage
--------
The frame is built from the single-season view, which carries all 30 clubs
every year from 2015 on. Savant serves earlier seasons too (2012 returns 30
rows); 2015+ is simply the range this package is exercised over.

Two kinds of NaN show up, both from the 3-year view, measured 2026-09-23
over 2015-2026 (360 rows):

* **8 rows have no 3-year window at all** because the park has no three-year
  history: 2017 ATL, 2018 ATL (Truist Park opened 2017), 2020 TEX, 2021 TEX
  (Globe Life Field opened 2020), 2020 TOR (Sahlen Field), 2025 OAK, 2026
  OAK (Sutter Health Park), 2025 TB (Steinbrenner Field). Every ``pf_3yr*``
  column is NaN on those rows while ``pf_1yr`` is still filled. Dropping
  those clubs instead would make a team vanish from a season with nothing in
  the output saying so.
* **``pf_xwobacon``, ``pf_xbacon`` and ``pf_hardhit`` are NaN for all 30
  clubs in 2015 and 2016** - 60 further rows - because their 3-year windows
  reach back to 2013 and 2014, before Statcast measured batted balls. Those
  three columns therefore have 68 NaN, not 8.
"""

from __future__ import annotations

import json
import re
import time
import warnings

import pandas as pd
import requests

_BASE_URL = (
    "https://baseballsavant.mlb.com/leaderboard/statcast-park-factors"
    "?type=year&year={year}"
    "&batSide=&stat=index_wOBA&condition=All"
    "&rolling={rolling}&parks=mlb"
)

# Savant embeds this leaderboard as a JSON literal in the page. It has no
# csv=true variant - csv=true returns the HTML page (measured 2026-09-23).
_DATA_RE = re.compile(r"var data = (\[.*?\]);", re.S)

# Say who we are. Claiming to be Chrome is what gets a python client served
# a Cloudflare challenge: measured 2026-09-23, fangraphs.com answers a
# "Mozilla/5.0 ... Chrome/140" UA with 403 + `cf-mitigated: challenge` and
# the same request with this kind of UA with 200.
_HEADERS = {
    "User-Agent": "savant-extras (+https://github.com/yasumorishima/savant-extras)",
}

# Savant club nickname -> abbreviation. Every nickname the feed emits for
# 2015-2026 is an exact key here; the substring match in _abbrev is a
# fallback for a wording change, not the normal path.
_NAME_TO_ABB: dict[str, str] = {
    "Angels":        "LAA",
    "Astros":        "HOU",
    "Athletics":     "OAK",   # also used for the Sacramento Athletics, 2025+
    "Blue Jays":     "TOR",
    "Braves":        "ATL",
    "Brewers":       "MIL",
    "Cardinals":     "STL",
    "Cubs":          "CHC",
    "D-backs":       "ARI",   # what the feed emits
    "Diamondbacks":  "ARI",   # alias: not emitted by Savant as of 2026-09-23
    "Dodgers":       "LAD",
    "Giants":        "SF",
    "Guardians":     "CLE",   # emitted for pre-2022 seasons too
    "Indians":       "CLE",   # alias: not emitted by Savant as of 2026-09-23
    "Mariners":      "SEA",
    "Marlins":       "MIA",
    "Mets":          "NYM",
    "Nationals":     "WAS",
    "Orioles":       "BAL",
    "Padres":        "SD",
    "Phillies":      "PHI",
    "Pirates":       "PIT",
    "Rangers":       "TEX",
    "Rays":          "TB",
    "Red Sox":       "BOS",
    "Reds":          "CIN",
    "Rockies":       "COL",
    "Royals":        "KC",
    "Tigers":        "DET",
    "Twins":         "MIN",
    "White Sox":     "CWS",
    "Yankees":       "NYY",
}

# Savant key -> clean column name. index_runs is handled on its own because
# it is the one metric published for both windows.
_INDEX_RENAME: dict[str, str] = {
    "index_hr":        "pf_hr",
    "index_1b":        "pf_1b",
    "index_2b":        "pf_2b",
    "index_3b":        "pf_3b",
    "index_so":        "pf_so",
    "index_bb":        "pf_bb",
    "index_obp":       "pf_obp",
    "index_hits":      "pf_hits",
    "index_woba":      "pf_woba",
    "index_wobacon":   "pf_wobacon",
    "index_xwobacon":  "pf_xwobacon",
    "index_bacon":     "pf_bacon",
    "index_xbacon":    "pf_xbacon",
    "index_hardhit":   "pf_hardhit",
    "index_wobatto":   "pf_wobatto",
}

_COLUMN_ORDER = (
    ["season", "team", "venue_id", "venue_name", "n_pa_1yr", "n_pa_3yr",
     "pf_1yr", "pf_3yr", "pf_3yr_years"]
    + list(_INDEX_RENAME.values())
)

_TEXT_COLS = ("team", "venue_name", "pf_3yr_years")

# Columns forced to float64 so a season with a gap and a season without one
# have the same dtype. season stays an int, n_pa_1yr is always present.
_FLOAT_COLS = tuple(c for c in _COLUMN_ORDER
                    if c not in _TEXT_COLS + ("season", "venue_id", "n_pa_1yr"))


def _abbrev(name: str) -> str | None:
    """Club nickname -> abbreviation, exact key first, then substring."""
    key = str(name).strip()
    if key in _NAME_TO_ABB:
        return _NAME_TO_ABB[key]
    for candidate, abb in _NAME_TO_ABB.items():
        if candidate in key:
            return abb
    return None


def _fetch_rows(year: int, rolling: str) -> list[dict]:
    """One Savant request. ``rolling`` is "" (3-year window) or "1" (single)."""
    url = _BASE_URL.format(year=year, rolling=rolling)
    resp = requests.get(url, headers=_HEADERS, timeout=30)
    resp.raise_for_status()

    match = _DATA_RE.search(resp.text)
    if match is None:
        raise ValueError(
            f"Park factor data block not found for {year} "
            f"(rolling={rolling!r}). The Savant page may have changed."
        )
    rows = json.loads(match.group(1))
    if not rows:
        raise ValueError(f"Savant returned an empty park factor table for {year}.")

    # The page decides which season it serves. If it disagrees with what we
    # asked for, the rows would still be labelled `season=year` downstream,
    # which is the kind of wrong that never announces itself.
    served = {str(r.get("key_year")) for r in rows}
    if served != {str(year)}:
        raise ValueError(
            f"Asked Savant for {year} (rolling={rolling!r}) and got "
            f"key_year {sorted(served)}."
        )

    missing_keys = sorted(set(_INDEX_RENAME) - set(rows[0]))
    if missing_keys:
        # A renamed Savant key would otherwise leave that column entirely
        # NaN, which is indistinguishable from "Statcast has no value for
        # this era" (2015-2016 xwOBAcon etc.).
        raise ValueError(
            f"Savant no longer sends {missing_keys} for {year} "
            f"(rolling={rolling!r}); the column map needs updating."
        )
    return rows


def _fetch_one(year: int) -> pd.DataFrame:
    """Fetch one season and return the tidy frame.

    The single-season view drives the frame because it carries all 30 clubs
    every year; the 3-year view is joined onto it by venue id and leaves
    NaN where a park has no three-year history.
    """
    single = _fetch_rows(year, "1")
    multi = _fetch_rows(year, "")

    by_venue = {row.get("venue_id"): row for row in multi}

    records = []
    for row in single:
        team = _abbrev(row.get("name_display_club"))
        if team is None:
            # A venue Savant lists without a club this package can name
            # (neutral site). Dropping it keeps "one row per club" true.
            continue
        if "venue_id" not in row:
            raise ValueError(
                f"Savant sent a {year} row with no venue_id "
                f"({row.get('name_display_club')!r}); the join key is gone."
            )
        three = by_venue.get(row["venue_id"], {})
        rec = {
            "season": year,
            "team": team,
            "venue_id": row.get("venue_id"),
            "venue_name": row.get("venue_name"),
            "n_pa_1yr": row.get("n_pa"),
            "n_pa_3yr": three.get("n_pa"),
            "pf_1yr": row.get("index_runs"),
            "pf_3yr": three.get("index_runs"),
            "pf_3yr_years": three.get("year_range"),
        }
        for savant_key, clean in _INDEX_RENAME.items():
            rec[clean] = three.get(savant_key)
        records.append(rec)

    df = pd.DataFrame.from_records(records)
    if df.empty:
        raise ValueError(
            f"No park factor row for {year} could be matched to a club. "
            f"Savant club names may have changed."
        )

    df["season"] = df["season"].astype("int64")
    df["venue_id"] = pd.to_numeric(df["venue_id"], errors="coerce").astype("int64")
    df["n_pa_1yr"] = pd.to_numeric(df["n_pa_1yr"], errors="coerce").astype("int64")
    for col in _FLOAT_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("float64")

    return df[_COLUMN_ORDER].sort_values("team").reset_index(drop=True)


def park_factors(season: int) -> pd.DataFrame:
    """
    Park factors for one MLB season, from Baseball Savant.

    Parameters
    ----------
    season : int
        MLB season year. 2015+ is the exercised range; earlier seasons are
        served too.

    Returns
    -------
    pd.DataFrame
        One row per club, sorted by ``team``. See the module docstring for
        the columns and for where the NaN are.

    Raises
    ------
    ValueError
        If the Savant page no longer carries the expected data block, serves
        a season other than the one asked for, drops a column this package
        maps, or returns no club this package can name.
    requests.HTTPError
        If the Baseball Savant request fails.

    Examples
    --------
    >>> from savant_extras import park_factors
    >>> df = park_factors(2024)
    >>> df[df["team"] == "COL"][["team", "pf_3yr", "pf_1yr", "pf_hr"]]
      team  pf_3yr  pf_1yr  pf_hr
    7  COL   125.0   121.0  109.0
    """
    return _fetch_one(season)


def park_factors_range(start_season: int, end_season: int,
                       sleep: float = 1.5) -> pd.DataFrame:
    """
    Park factors for several seasons, concatenated.

    A season that fails is reported and skipped rather than sinking the
    whole range; the skipped seasons come back as a ``UserWarning`` so a
    caller can notice without reading stdout.

    Parameters
    ----------
    start_season : int
        First season (e.g. 2015).
    end_season : int
        Last season (e.g. 2026).
    sleep : float, default 1.5
        Seconds to wait between seasons. Each season costs two requests
        (the 3-year window and the single year); the wait goes between
        seasons, not between those two.

    Returns
    -------
    pd.DataFrame
        ``(end_season - start_season + 1) * 30`` rows when every season
        succeeds; an empty DataFrame when none does.

    Examples
    --------
    >>> from savant_extras import park_factors_range
    >>> df = park_factors_range(2020, 2024)
    >>> df["season"].nunique()
    5
    """
    frames: list[pd.DataFrame] = []
    failures: list[str] = []
    for year in range(start_season, end_season + 1):
        try:
            df = _fetch_one(year)
            frames.append(df)
            print(f"  park_factors {year}: {len(df)} clubs fetched")
        except Exception as exc:
            failures.append(f"{year} ({exc})")
            print(f"  park_factors {year}: FAILED - {exc}")
        if year < end_season:
            time.sleep(sleep)

    if not frames:
        warnings.warn(
            "park_factors_range: no data fetched for any season. "
            "Baseball Savant may be unreachable from this network. "
            "Returning empty DataFrame.",
            UserWarning,
            stacklevel=2,
        )
        return pd.DataFrame()
    if failures:
        warnings.warn(
            "park_factors_range: skipped " + "; ".join(failures),
            UserWarning,
            stacklevel=2,
        )
    return pd.concat(frames, ignore_index=True)
