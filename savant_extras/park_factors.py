"""
MLB Park Factors from FanGraphs.

Provides per-season, per-team park factors for all 30 MLB ballparks.
Data source: FanGraphs Guts! (https://www.fangraphs.com/guts.aspx?type=pf)

Columns returned
----------------
season      : int   — MLB season year
team        : str   — FanGraphs team abbreviation (COL, BOS, ...)
pf_5yr      : float — 5-year basic park factor (runs)
pf_3yr      : float — 3-year basic park factor (runs)
pf_1yr      : float — single-year park factor (runs)
pf_hr       : float — HR park factor
pf_1b       : float — 1B park factor
pf_2b       : float — 2B park factor
pf_3b       : float — 3B park factor
pf_so       : float — SO park factor
pf_bb       : float — BB park factor
pf_fip      : float — FIP-based park factor

All factors: 100 = neutral, >100 = hitter-friendly, <100 = pitcher-friendly.
For pitching park factor, values are inverted (Coors is bad for pitchers).
"""

from __future__ import annotations

import time

import pandas as pd
import requests

_BASE_URL = "https://www.fangraphs.com/guts.aspx?type=pf&teamid=0&season={year}"

# FanGraphs team nickname → FanGraphs abbreviation
# (matches what pybaseball batting_stats / pitching_stats returns in "Team" column)
_NAME_TO_ABB: dict[str, str] = {
    "Angels":        "LAA",
    "Astros":        "HOU",
    "Athletics":     "OAK",   # also used for Sacramento Athletics 2025+
    "Blue Jays":     "TOR",
    "Braves":        "ATL",
    "Brewers":       "MIL",
    "Cardinals":     "STL",
    "Cubs":          "CHC",
    "Diamondbacks":  "ARI",
    "D-backs":       "ARI",
    "Dodgers":       "LAD",
    "Giants":        "SF",
    "Guardians":     "CLE",
    "Indians":       "CLE",   # renamed → Guardians in 2022
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

# Column rename mapping: FanGraphs HTML header → clean name
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

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    ),
    "Referer": "https://www.fangraphs.com/",
}


def _abbrev(name: str) -> str | None:
    """チーム名（部分一致）→ FanGraphs略称"""
    for key, abb in _NAME_TO_ABB.items():
        if key in str(name):
            return abb
    return None


def _fetch_one(year: int) -> pd.DataFrame:
    """1シーズン分のパークファクターを取得して DataFrame で返す"""
    url = _BASE_URL.format(year=year)
    resp = requests.get(url, headers=_HEADERS, timeout=20)
    resp.raise_for_status()

    # HTML から全テーブルを取得し、Team 列がある最初のものを使う
    tables = pd.read_html(resp.text)
    target = None
    for t in tables:
        flat_cols = [str(c).strip() for c in t.columns]
        if any("Team" in c for c in flat_cols):
            target = t
            break

    if target is None:
        raise ValueError(f"Park factor table not found for {year}. "
                         f"Page may have changed structure.")

    # 列名をフラット化 (MultiIndex 対応)
    target.columns = [
        str(c[-1]).strip() if isinstance(c, tuple) else str(c).strip()
        for c in target.columns
    ]

    # Team 列の特定とチーム略称化
    team_col = next((c for c in target.columns if c == "Team"), None)
    if team_col is None:
        raise ValueError(f"'Team' column not found for {year}. "
                         f"Columns: {target.columns.tolist()}")

    target = target.rename(columns=_COL_RENAME)
    target["team"] = target[team_col].apply(_abbrev)
    target["season"] = year

    # 不要行（NaN team, 合計行など）を除去
    target = target.dropna(subset=["team"])

    # 存在する PF 列だけ選択
    keep = ["season", "team"] + [c for c in _PF_COLS if c in target.columns]
    target = target[keep].copy()

    # 数値変換（"--" や空文字 → NaN）
    for col in target.columns:
        if col not in ("season", "team"):
            target[col] = pd.to_numeric(target[col], errors="coerce")

    return target.reset_index(drop=True)


def park_factors(season: int) -> pd.DataFrame:
    """
    指定シーズンの MLB パークファクターを取得する。

    Parameters
    ----------
    season : int
        MLB シーズン年（例: 2024）

    Returns
    -------
    pd.DataFrame
        30チーム分のパークファクター。
        列: season, team, pf_5yr, pf_3yr, pf_1yr, pf_hr, pf_1b, pf_2b, pf_3b, pf_so, pf_bb, pf_fip

    Examples
    --------
    >>> from savant_extras import park_factors
    >>> df = park_factors(2024)
    >>> df[df["team"] == "COL"][["team", "pf_5yr", "pf_hr"]]
       team  pf_5yr  pf_hr
    5   COL     116    131
    """
    return _fetch_one(season)


def park_factors_range(start_season: int, end_season: int,
                       sleep: float = 1.5) -> pd.DataFrame:
    """
    複数シーズンのパークファクターを取得して結合する。

    Parameters
    ----------
    start_season : int
        開始シーズン（例: 2015）
    end_season : int
        終了シーズン（例: 2025）
    sleep : float
        リクエスト間の待機秒数（デフォルト 1.5）

    Returns
    -------
    pd.DataFrame
        (end_season - start_season + 1) × 30 行のパークファクター。

    Examples
    --------
    >>> from savant_extras import park_factors_range
    >>> df = park_factors_range(2020, 2024)
    >>> df.shape[0]  # 5 seasons × 30 teams
    150
    """
    frames: list[pd.DataFrame] = []
    for year in range(start_season, end_season + 1):
        try:
            df = _fetch_one(year)
            frames.append(df)
            print(f"  park_factors {year}: {len(df)} teams fetched")
        except Exception as exc:
            print(f"  park_factors {year}: FAILED — {exc}")
        if year < end_season:
            time.sleep(sleep)

    if not frames:
        raise RuntimeError(
            "No park factor data fetched. "
            "Check network connectivity or FanGraphs page structure."
        )
    return pd.concat(frames, ignore_index=True)
