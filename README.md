# savant-extras

**Baseball Savant leaderboard data — complements pybaseball.**

[pybaseball](https://github.com/jldbc/pybaseball) is great but many Baseball Savant leaderboards are missing or limited. `savant-extras` fills that gap with **17 leaderboards** covering batting, pitching, catching, baserunning, fielding, and park factors — all as simple one-line function calls returning DataFrames.

## Installation

```bash
pip install savant-extras
```

## Quick Start

```python
from savant_extras import (
    bat_tracking, pitch_tempo, arm_strength,
    pitch_movement, swing_take, catcher_throwing,
)

# Bat tracking with custom date range (2024+)
df = bat_tracking("2024-04-01", "2024-04-30")

# Pitcher pitch tempo
df = pitch_tempo(2024)

# Outfielder arm strength
df = arm_strength(2024, position="Outfielder")

# Slider movement
df = pitch_movement(2024, pitch_type="SL")

# Batter plate discipline
df = swing_take(2024)

# Catcher pop time & CS rate
df = catcher_throwing(2024)
```

## All Functions

Every leaderboard function returns a `pd.DataFrame`. Most have a `_range()` variant for multi-season queries (adds a `year` column).

### Batting

| Function | Data from | Description |
|---|---|---|
| `bat_tracking(start_date, end_date)` | 2024+ | Bat speed, attack angle, swing tilt (custom date range) |
| `bat_tracking_monthly(year)` | 2024+ | Monthly bat tracking (Apr–Oct) |
| `bat_tracking_splits(year)` | 2024+ | First-half / second-half splits |
| `batted_ball(year)` | — | GB/FB/LD rates, pull/oppo splits |
| `home_runs(year)` | — | HR distance, exit velocity, xHR, no-doubters |
| `swing_take(year)` | — | Run values by zone (heart/shadow/chase/waste) |
| `year_to_year(year)` | — | xwOBA changes across seasons |

### Pitching

| Function | Data from | Description |
|---|---|---|
| `pitch_tempo(year)` | 2010+ | Pace metrics (median seconds, hot/warm/cold) |
| `pitch_movement(year)` | — | Horizontal/vertical break by pitch type |
| `pitcher_arm_angle(year)` | — | Release point angles and positions |
| `running_game(year)` | — | Pitcher running game (pickoffs, CS above avg) |
| `timer_infractions(year)` | 2023+ | Pitch clock violations |

### Catching

| Function | Data from | Description |
|---|---|---|
| `catcher_blocking(year)` | — | Blocks above average, PB/WP prevention |
| `catcher_throwing(year)` | — | Pop time, exchange time, CS rate, arm strength |
| `catcher_stance(year)` | — | One-knee vs traditional: framing, blocking, throwing |

### Baserunning & Fielding

| Function | Data from | Description |
|---|---|---|
| `arm_strength(year)` | 2020+ | Fielder throw speed by position |
| `baserunning(year)` | — | Total baserunning run value (XB + SB) |
| `basestealing(year)` | — | Stolen base run value, lead distances |

### Park Factors

| Function | Data from | Description |
|---|---|---|
| `park_factors(season)` | 2015+ | Ballpark run factors per club, 1-year and 3-year windows (Baseball Savant) |
| `park_factors_range(start, end)` | 2015+ | Multi-season park factors concatenated |
| `park_factors_fangraphs(season)` | 2015+ | FanGraphs Guts! park factors - the only source here for `pf_5yr` and `pf_fip` |
| `park_factors_fangraphs_range(start, end)` | 2015+ | Multi-season FanGraphs park factors |

Columns returned: `season`, `team`, `venue_id`, `venue_name`, `n_pa_1yr`, `n_pa_3yr`, `pf_1yr`, `pf_3yr`, `pf_3yr_years`, `pf_hr`, `pf_1b`, `pf_2b`, `pf_3b`, `pf_so`, `pf_bb`, `pf_obp`, `pf_hits`, `pf_woba`, `pf_wobacon`, `pf_xwobacon`, `pf_bacon`, `pf_xbacon`, `pf_hardhit`, `pf_wobatto`.
All factors: 100 = neutral, >100 = hitter-friendly, <100 = pitcher-friendly.
Every column except `pf_1yr` and `n_pa_1yr` comes from the 3-year window; `pf_3yr_years` records which window that was.

All 30 clubs appear in every season, and every factor column is float64 in every season.
Two kinds of NaN come from the 3-year view (measured 2026-09-23 over 2015-2026, 360 rows):

- **8 rows have no 3-year window at all**, because the park has no three-year history:
  2017 ATL, 2018 ATL, 2020 TEX, 2020 TOR, 2021 TEX, 2025 OAK, 2025 TB, 2026 OAK.
  Their `pf_3yr*` columns are NaN while `pf_1yr` is still filled.
- **`pf_xwobacon`, `pf_xbacon` and `pf_hardhit` are NaN for all 30 clubs in 2015 and 2016**
  (60 further rows), because those 3-year windows reach back before Statcast measured
  batted balls. Those three columns have 68 NaN, not 8.

> **Source changed in 0.5.0.** Through 0.4.4 `park_factors()` scraped FanGraphs Guts!, in a package
> whose every other function reads Baseball Savant. It now reads Savant too. The FanGraphs table is
> still here as `park_factors_fangraphs()`, which is the only way to get `pf_5yr` and `pf_fip`.
>
> **Columns kept their names but changed their meaning.** `pf_hr`, `pf_1b`, `pf_2b`, `pf_3b`,
> `pf_so`, `pf_bb` and the runs factor come from Savant's index now, and the two scales disagree:
> COL 2024 is `pf_hr` 109 here and 131 on the FanGraphs scale. Pin `savant-extras<0.5` or call
> `park_factors_fangraphs()` if you need the old numbers.
>
> The old implementation sent a Chrome User-Agent, and that is what FanGraphs challenges: measured
> 2026-09-23 from a residential line, a `Chrome/140` UA gets 403 + `cf-mitigated: challenge` while
> `curl`, no UA, and this package's own UA all get 200. `park_factors_fangraphs()` says who it is
> instead. Datacenter addresses are blocked separately - pybaseball, which sends the honest default
> UA, still got 403 for all 12 seasons on a GitHub runner (2026-09-21), so expect the FanGraphs
> functions to work from a home connection and not from a cloud runner.

```python
from savant_extras import park_factors, park_factors_range

# Single season
df = park_factors(2024)
print(df[df["team"] == "COL"][["team", "pf_3yr", "pf_1yr", "pf_hr"]])
#   team  pf_3yr  pf_1yr  pf_hr
# 7  COL   125.0   121.0  109.0

# Multi-season (e.g. for model training)
df = park_factors_range(2020, 2025)
print(df["season"].nunique())  # 6
```

### Common Parameters

| Parameter | Type | Description |
|---|---|---|
| `player_type` | str | `"batter"` or `"pitcher"` (where applicable) |
| `min_*` | int or str | Minimum qualifier. Pass an int (e.g. `min_pa=100`) or `"q"` to apply the MLB standard qualifier automatically. |
| `position` | str | Position filter (arm_strength): `""`, `"RF"`, `"SS"`, etc. |
| `pitch_type` | str | Pitch type filter (pitch_movement): `"FF"`, `"SL"`, etc. |

### Multi-Season Queries

Most functions have a `_range(start_year, end_year)` variant:

```python
from savant_extras import pitch_tempo_range, arm_strength_range

# Compare pitch tempo pre/post pitch clock
df = pitch_tempo_range(2022, 2024)

# 5 years of arm strength
df = arm_strength_range(2020, 2024)
```

## Demo App

**[MLB Bat Tracking Dashboard](https://yasumorishima-mlb-bat-tracking.streamlit.app/)** — built with savant-extras ([source](https://github.com/yasumorishima/mlb-bat-tracking-dashboard))

## Why savant-extras?

| Leaderboard | pybaseball | savant-extras |
|---|---|---|
| Bat tracking (date range) | Full season only | Custom date ranges |
| Pitch tempo | Not supported | ✅ |
| Arm strength | Not supported | ✅ |
| Batted ball profile | Not supported | ✅ |
| Home runs | Not supported | ✅ |
| Pitch movement | Not supported | ✅ |
| Swing & take | Not supported | ✅ |
| Year-to-year changes | Not supported | ✅ |
| Pitcher arm angle | Not supported | ✅ |
| Running game (pitcher) | Not supported | ✅ |
| Catcher blocking | Not supported | ✅ |
| Catcher throwing | Not supported | ✅ |
| Catcher stance | Not supported | ✅ |
| Baserunning run value | Not supported | ✅ |
| Basestealing run value | Not supported | ✅ |
| Timer infractions | Not supported | ✅ |
| Park factors (Statcast) | Not supported | ✅ |

## Known Issues

- **`swing_take()`**: Baseball Savant の Swing & Take リーダーボードの CSV エンドポイントに障害中（ヘッダーのみ、データ行なし）。現在は空の DataFrame が返ります。上流 API が復旧次第、コード変更なしで動作します。代替として `batted_ball()` や `year_to_year()` を使用してください。

## Cloud Environment Notes

Every function in this package except the two `*_fangraphs` ones reads Baseball Savant, which answers cloud runners (Kaggle, Google Colab, GitHub Actions) the same way it answers a laptop. Before 0.5.0 `park_factors()` read FanGraphs and returned 403 from those environments; that is no longer the case.

`park_factors_fangraphs()` still depends on FanGraphs, which blocks datacenter addresses — measured on a GitHub runner 2026-09-21, where pybaseball got 403 for all 12 seasons despite sending the honest default User-Agent. Run it from a home connection and save the result:

```python
from savant_extras import park_factors_fangraphs_range
df = park_factors_fangraphs_range(2024, 2025)
df.to_csv("park_factors_fg.csv", index=False)
```

If a fetch fails for every season, both `*_range` functions return an empty DataFrame with a warning rather than raising, and a partial failure warns with the seasons it skipped.

In Kaggle notebooks, `pybaseball` is not pre-installed. Install both explicitly:

```python
!pip install savant-extras pybaseball
```

## License

MIT
